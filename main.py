#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import json
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import auth_client as AUTH
import link_generator as LG

FALLBACK_SERVICES = [3]
MAX_ROUNDS = 3
MAX_ROUNDS_HARD_CAP = 12
POLL_MAX_ATTEMPTS = 10
POLL_INTERVAL = 0.1
POLL_OVERLAP_DELAY = 0.05
STEP_THROTTLE_RETRIES = 2
STEP_THROTTLE_SLEEP = 2.0
MIN_STEP_GAP = 5.0

class Timer:
    def __init__(self):
        self.phases = {}
        self.t0 = None
        self.current_phase = None
        self.invalid_reason = None

    def start(self, phase):
        if self.current_phase is not None:
            self.stop()
        self.current_phase = phase
        self.t0 = time.time()

    def stop(self):
        if self.current_phase is not None and self.t0 is not None:
            dt = time.time() - self.t0
            self.phases[self.current_phase] = self.phases.get(self.current_phase, 0.0) + dt
            self.current_phase = None
            self.t0 = None

    def add(self, name, seconds):
        self.phases[name] = self.phases.get(name, 0.0) + seconds

    def total(self):
        return sum(self.phases.values())

def resolve_meta(ticket, session=None, verbose=False):
    cp = None
    try:
        meta = AUTH.get_session_metadata(ticket, session=session)
        if isinstance(meta, dict):
            if meta.get('success') is False and not meta.get('transient'):
                msg = str(meta.get('message') or meta.get('error') or '').lower()
                if any(m in msg for m in AUTH.INVALID_MARKERS):
                    reason = str(meta.get('message') or meta.get('error') or 'invalid link')
                    return None, cp, False, reason
            data = meta.get('data', meta)
            if isinstance(data, dict):
                profile = data.get('activeRevenueProfile', {})
                if isinstance(profile, dict) and 'service' in profile:
                    svc = int(profile['service'])
                    try:
                        cpn = profile.get('checkpointCount')
                        cp = int(cpn) if cpn else None
                    except (TypeError, ValueError):
                        cp = None
                    return svc, cp, True, None
    except Exception:
        pass
    return None, cp, True, None

def throttled(r):
    if not isinstance(r, dict):
        return False
    msg = ' '.join(str(r.get(k, '')) for k in ('message', 'error', 'detail')).lower()
    return ('too fast' in msg) or ('slow down' in msg) or ('too many' in msg)

def do_step_with_retry(ticket, service=None, session=None, verbose=False, timer=None,
                       gap_state=None, overlap_poll=False, poll_session=None):
    services_to_try = []
    if service is not None:
        services_to_try.append(service)
    for svc in FALLBACK_SERVICES:
        if svc not in services_to_try:
            services_to_try.append(svc)

    if timer:
        timer.start('step')

    if gap_state is not None and gap_state.get('ts'):
        gap = time.time() - gap_state['ts']
        if gap < MIN_STEP_GAP:
            time.sleep(MIN_STEP_GAP - gap)

    overlap_box = {}
    overlap_thread = None

    def overlap_poll_worker():
        time.sleep(POLL_OVERLAP_DELAY)
        sess = poll_session if poll_session is not None else session
        for _ in range(POLL_MAX_ATTEMPTS):
            if overlap_box.get('stop'):
                return
            try:
                st = AUTH.get_session_status(ticket, session=sess)
                data = st.get('data', st) if isinstance(st, dict) else {}
                k = data.get('key', '')
                if k and k != 'KEY_NOT_FOUND':
                    overlap_box['key'] = k
                    return
            except Exception:
                pass
            time.sleep(POLL_INTERVAL)

    for svc in services_to_try:
        for attempt in range(STEP_THROTTLE_RETRIES + 1):
            try:
                if overlap_poll and overlap_thread is None:
                    overlap_thread = threading.Thread(target=overlap_poll_worker, daemon=True)
                    overlap_thread.start()
                r = AUTH.do_step(ticket, service=svc, session=session)
                if gap_state is not None:
                    gap_state['ts'] = time.time()
                if isinstance(r, dict) and r.get('success'):
                    if timer:
                        timer.stop()
                    return svc, r, overlap_box
                if throttled(r):
                    if attempt < STEP_THROTTLE_RETRIES:
                        time.sleep(STEP_THROTTLE_SLEEP)
                        continue
                break
            except Exception:
                break

    if timer:
        timer.stop()
    overlap_box['stop'] = True
    return None, {'success': False, 'error': 'all services failed'}, overlap_box

def check_key_in_response(ticket, session=None, verbose=False, timer=None):
    try:
        if timer:
            timer.start('poll')
        st = AUTH.get_session_status(ticket, session=session)
        if timer:
            timer.stop()
        st_data = st.get('data', st) if isinstance(st, dict) else {}
        key = st_data.get('key', '')
        if key and key != 'KEY_NOT_FOUND':
            return key
    except Exception:
        pass
    return None

def poll_for_key(ticket, session=None, max_attempts=3, interval=0, verbose=False, timer=None):
    for i in range(max_attempts):
        key = check_key_in_response(ticket, session=session, verbose=verbose, timer=timer)
        if key:
            return key
        if interval > 0 and i < max_attempts - 1:
            time.sleep(interval)
    return None

def solve_chain(ticket, verbose=False, max_rounds=MAX_ROUNDS, session=None):
    if session is None:
        session = AUTH.create_session()
    current_ticket = ticket
    current_service = None
    timer = Timer()
    invalid_reason = [None]
    round_cap = max(max_rounds, 1)
    round_idx = 0
    last_exit = ['round-exhausted']
    gap_state = {'ts': 0.0}

    while round_idx < round_cap:
        if timer:
            timer.start('meta')
        meta_session = AUTH.create_session()
        meta_future = None
        stat_future = None
        cpc = None
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                meta_future = pool.submit(resolve_meta, current_ticket, meta_session, False)

                if round_idx == 0:
                    stat_session = AUTH.create_session()
                    stat_future = pool.submit(check_key_in_response, current_ticket,
                                              stat_session, False, None)

                if stat_future is not None:
                    try:
                        early = stat_future.result(timeout=6)
                    except Exception:
                        early = None
                    if early:
                        return early, timer

                try:
                    svc, cpc, mvalid, mreason = meta_future.result(timeout=6)
                    current_service = svc
                    if not mvalid:
                        invalid_reason[0] = mreason
                        last_exit[0] = 'invalid-link'
                        timer.invalid_reason = mreason
                        return None, timer
                except Exception:
                    current_service, cpc = None, None
        finally:
            meta_session.close()
            try:
                if stat_future is not None:
                    stat_session.close()
            except Exception:
                pass
        if timer:
            timer.stop()

        if cpc is not None:
            need = cpc + 1
            if need > round_cap:
                round_cap = min(need, MAX_ROUNDS_HARD_CAP)

        last_step = round_idx > 0
        service, resp, overlap = do_step_with_retry(
            current_ticket,
            service=current_service,
            session=session,
            verbose=False,
            timer=timer,
            gap_state=gap_state,
            overlap_poll=last_step,
            poll_session=None
        )
        if overlap.get('key'):
            return overlap['key'], timer
        if service is None:
            last_exit[0] = 'step-failed'
            round_idx += 1
            continue

        current_service = service
        url = (resp.get('data') or {}).get('url', '')
        if not url:
            last_exit[0] = 'no-url'
            round_idx += 1
            continue

        if url == 'about:blank':
            key = poll_for_key(current_ticket, session=session, verbose=False, timer=timer,
                               max_attempts=POLL_MAX_ATTEMPTS, interval=POLL_INTERVAL)
            if key:
                return key, timer
            last_exit[0] = 'poll-timeout'
            round_idx += 1
            continue

        callback = AUTH.decode_callback_url(url)
        if callback:
            next_ticket = AUTH.extract_ticket_from_callback(callback)
            if next_ticket and len(next_ticket) > 50:
                current_ticket = next_ticket
                round_idx += 1
                continue

        key = check_key_in_response(current_ticket, session=session, verbose=False, timer=timer)
        if key:
            return key, timer
        last_exit[0] = 'no-callback-no-key'
        break

    key = check_key_in_response(current_ticket, session=session, verbose=False, timer=timer)
    if key:
        return key, timer

    return None, timer

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('target', nargs='?')
    ap.add_argument('--generate', '-g', type=int, default=0)
    ap.add_argument('--quiet', '-q', action='store_true', default=True)
    ap.add_argument('--max-rounds', type=int, default=MAX_ROUNDS)
    ap.add_argument('--no-auto', action='store_true')
    args = ap.parse_args()

    AUTH.start_version_watcher()

    tickets = []
    if args.generate > 0:
        try:
            urls = LG.batch_links(args.generate)
            tickets = [AUTH.extract_ticket(u) for u in urls]
        except Exception:
            sys.exit(1)
    elif args.target:
        tickets.append(AUTH.extract_ticket_from_arg(args.target))
    else:
        sys.exit(1)

    if args.no_auto:
        for t in tickets:
            print(f'https://auth.platorelay.com/a?d={t}')
        return

    for ticket in tickets:
        key, timer = solve_chain(ticket, verbose=False, max_rounds=args.max_rounds, session=None)
        if key:
            print(f"تم تجاوز الرابط بنجاح ✅\nالمفتاح: {key}")
        else:
            print("فشل في تجاوز الرابط أو جلب المفتاح ❌")

if __name__ == '__main__':
    main()
