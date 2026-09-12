#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import base64
import itertools
import random
import string
import threading
import time
import urllib.parse
import requests
import urllib3
from Crypto.Cipher import AES as AES
# fake_useragent 是可选依赖:没有它就用下面这条固定的 iPhone UA,功能不受影响。
# fake_useragent is optional: without it we fall back to the fixed iPhone UA below.
try:
    from fake_useragent import UserAgent

    UA_SOURCES = (
        UserAgent(browsers=['Mobile Safari'], platforms='mobile'),
        UserAgent(browsers=['Chrome Mobile'], platforms='mobile', min_version=100.0),
    )
except Exception:  # ImportError 及其内部初始化异常都按缺失处理
    UA_SOURCES = ()

AUTH_API = "https://auth.platorelay.com/api"

# ---------------------------------------------------------------------------
# 客户端版本号：自动跟上上游
#
# 提交时带的 x-client-version 得跟上游网页客户端一致，旧了会被直接拒绝
# （"outdated client"）。写死在代码里，上游一升级就得手动跟着改 —— 漏改一次
# 服务就全线停摆。所以自动拿：
#
# 1. 抓入口页 HTML（约 500B），抠出 /assets/index-<hash>.js 的地址
# 2. Range 请求只取脚本前 256KB（版本号实测在前 128KB 里，2MB 全量省掉 87%）
# 3. 从引号包裹的字符串里抠出所有形如 x.y.z 的候选
# 4. 逐个用假 ticket 探测：版本太旧回 "outdated client"，版本可用回别的错
#    （假 ticket 本身无效的那种）。探测零成本：不碰真实会话、不占求解名额
#
# 脚本内容用完即弃：候选一提取出来就释放，不落盘，内存里只留几字节的版本号。
# 全部候选失败时退回 FALLBACK_VERSION。缓存 1 小时，刷新只发生在后台线程。
# ---------------------------------------------------------------------------
APP_URL = "https://auth.platorelay.com/a"
FALLBACK_VERSION = "5.4.0"
VER_TTL = 3600.0  # 版本缓存秒数

_client_version = FALLBACK_VERSION
_client_version_at = time.time()  # 启动即视为新鲜:首请求用兜底值,刷新交给后台线程
_ver_lock = threading.Lock()


def _http_get(url, headers=None):
    # 紧超时：版本提取挂了不能拖慢提交路径
    try:
        r = requests.get(url, headers=headers or {}, timeout=8)
        if r.status_code != 200:
            return None
        return r.text
    except Exception:
        return None


def _version_candidates(text):
    # 从引号包裹的字符串里抠 x.y.z 形状的候选（三段纯数字）
    found = []
    i = 0
    data = text
    n = len(data)
    while i < n:
        if data[i] == "'":
            j = data.find("'", i + 1)
            if j < 0:
                break
            token = data[i + 1:j]
            parts = token.split('.')
            if (len(parts) == 3
                    and all(p.isdigit() for p in parts)
                    and token not in found):
                found.append(token)
            i = j + 1
            continue
        i += 1
    return found


def _version_works(version, ua):
    # 假 ticket 探测：格式合法但不指向任何真会话。
    # 服务器先查版本后查票 —— outdated = 版本不行，invalid payload = 版本过了。
    letters = string.ascii_letters + string.digits
    fake = ''.join(random.choice(letters) for _ in range(64))
    built = build_meta_stream(fake, user_agent=ua)
    if built is None:
        return False
    meta, stream = built
    url = f"{AUTH_API}/session/step?ticket={urllib.parse.quote(fake)}&service=3"
    body = json.dumps({"captcha": None, "meta": meta, "stream": stream, "resolved": True}).encode()
    try:
        r = step_pool.request('PUT', url, body=body, redirect=False, headers={
            'User-Agent': ua,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-client-name': 'platoboost webclient',
            'x-client-version': version,
        })
        return b'outdated client' not in r.data
    except Exception:
        return False


def _refresh_client_version():
    global _client_version, _client_version_at
    try:
        html = _http_get(APP_URL, {'User-Agent': FALLBACK_UA})
        if not html:
            return
        i = html.find('/assets/index-')
        if i < 0:
            return
        j = html.find('"', i)
        if j < 0:
            return
        script_url = 'https://auth.platorelay.com' + html[i:j]

        # 先 Range 取前 256KB，找不到候选再全量兜底
        candidates = []
        try:
            r = requests.get(script_url, headers={
                'User-Agent': FALLBACK_UA, 'Range': 'bytes=0-262143'
            }, timeout=8)
            if r.status_code == 200 or r.status_code == 206:
                candidates = _version_candidates(r.text)
        except Exception:
            pass
        if not candidates:
            body = _http_get(script_url, {'User-Agent': FALLBACK_UA})
            if body:
                candidates = _version_candidates(body)
        if not candidates:
            return

        ua = FALLBACK_UA
        for cand in candidates:
            if _version_works(cand, ua):
                global_set(cand)
                return
    except Exception:
        pass


def global_set(version):
    global _client_version, _client_version_at
    if version != _client_version:
        print(f'[版本] 客户端版本更新: {_client_version} -> {version}', flush=True)
    _client_version = version
    _client_version_at = time.time()


def client_version():
    # 纯读缓存。刷新只发生在后台线程，提交路径绝不被版本提取拖慢。
    global _client_version_at
    if time.time() - _client_version_at > VER_TTL:
        # 过期了就在本线程刷一次（带锁防并发重复刷）
        if _ver_lock.acquire(blocking=False):
            try:
                if time.time() - _client_version_at > VER_TTL:
                    _refresh_client_version()
                    _client_version_at = time.time()
            finally:
                _ver_lock.release()
    return _client_version


def start_version_watcher():
    # 后台线程：启动刷一次，之后每小时一次
    def worker():
        while True:
            try:
                _refresh_client_version()
                _client_version_at = time.time()
            except Exception:
                _client_version_at = time.time()
            time.sleep(VER_TTL)
    t = threading.Thread(target=worker, daemon=True)
    t.start()

# ticket 至少要这么长才能切出两组 AES 钥匙。
#
# 第二组从第 2 个字符起算、取到第 33 个（ticket[1:17] 和 ticket[17:33]），所以 33 是
# 硬下限。低于这个长度 Python 的切片不会报错，只会给出短的甚至空的钥匙，等到 AES 那
# 一步才炸 ValueError —— 而那时候验证码 token 已经拿到了，白烧一个。
MIN_TICKET_LEN = 33


# fake_useragent 每次取用约 16ms(内部重新筛选数据集),高并发下是显著开销:
# 启动时预生成一批,之后 O(1) 轮转取用 —— 对外表现(UA 多样性)不变。
UA_POOL = []
UA_IDX = itertools.count()
UA_SCREEN = {}

SCREENS_IPHONE = ('390x844', '393x852', '375x812', '414x896', '430x932', '428x926', '360x780')
SCREENS_IPAD = ('820x1180', '834x1194', '768x1024', '744x1133', '1024x1366')
SCREENS_ANDROID = ('360x800', '412x915', '393x873', '384x854', '360x780', '412x892', '432x960')

FALLBACK_UA = ('Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) '
               'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Mobile/15E148 Safari/604.1')


def screens_for(platform, os_name):
    p = (platform or '').lower()
    o = (os_name or '').lower()
    if 'ipad' in p or 'tablet' in p:
        return SCREENS_IPAD
    if 'iphone' in p or 'ipod' in p or 'ios' in o:
        return SCREENS_IPHONE
    return SCREENS_ANDROID


def build_ua_pool(size=32):
    #预生成 UA 池:从各来源均匀取用,并为每个 UA 绑定一个匹配其平台的屏幕分辨率
    # fake_useragent 缺失时 UA_SOURCES 为空,直接用固定 UA 兜底。
    pool = []
    if not UA_SOURCES:
        return [FALLBACK_UA]
    per = max(1, size // len(UA_SOURCES))
    for src in UA_SOURCES:
        got = 0
        tried = 0
        while got < per and tried < per * 8:
            tried += 1
            try:
                rec = src.getRandom
            except Exception:
                break
            if not isinstance(rec, dict):
                break
            s = rec.get('useragent')
            if not s or s in UA_SCREEN:
                continue
            cands = screens_for(rec.get('platform'), rec.get('os'))
            # 用 UA 字符串哈希取模,保证同一 UA 恒定拿到同一分辨率
            UA_SCREEN[s] = cands[hash(s) % len(cands)]
            pool.append(s)
            got += 1
    if not pool:
        pool = [FALLBACK_UA]
        UA_SCREEN.setdefault(FALLBACK_UA, SCREENS_IPHONE[0])
    return pool


def rand_ua():
    global UA_POOL
    if not UA_POOL:
        UA_POOL = build_ua_pool()
    return UA_POOL[next(UA_IDX) % len(UA_POOL)]


def pick_screen(user_agent):
    #返回与该 UA 绑定的屏幕分辨率;未知 UA 则按其字符串特征推断
    s = UA_SCREEN.get(user_agent)
    if s:
        return s
    low = (user_agent or '').lower()
    if 'ipad' in low:
        cands = SCREENS_IPAD
    elif 'iphone' in low or 'ipod' in low:
        cands = SCREENS_IPHONE
    else:
        cands = SCREENS_ANDROID
    return cands[hash(user_agent or '') % len(cands)]

#AES-CTR

def aes_ctr_encrypt(plaintext, key_bytes, iv_bytes):
    #对当前计数器进行加密
    key = bytearray(key_bytes) if isinstance(key_bytes, (bytes, bytearray)) else bytearray(key_bytes)
    iv = bytearray(iv_bytes) if isinstance(iv_bytes, (bytes, bytearray)) else bytearray(iv_bytes)
    data = plaintext.encode() if isinstance(plaintext, str) else plaintext
    out = bytearray()
    for i in range(0, len(data), 16):
        blk = AES.new(bytes(key), AES.MODE_ECB).encrypt(bytes(iv))
        out += bytes(a ^ b for a, b in zip(data[i:i + 16], blk))
        #递增计数器
        j = 15
        while True:
            iv[j] = (iv[j] + 1) & 0xFF
            if iv[j] != 0:
                break
            j -= 1
            if j < 0:
                break
    return bytes(out)


def build_meta_stream(ticket, now_ms=None, user_agent=None, screen=None):
    #从ticket构建AES-CTR字段。ticket 太短返回 None
    # user_agent: 加密体内声明的 UA。应与本次请求 HTTP 头的 User-Agent 保持一致,
    #   否则"头里是随机某机型、体内固定写死另一机型"会形成自相矛盾的指纹。
    # screen: 屏幕尺寸,默认按 UA 平台自动挑一个匹配值。
    #
    # 返回 None 而不是让它炸：Python 切片越界不报错,ticket 只有 8 个字符时
    # ticket[16:32] 直接给空串,一路带到 AES 才抛 ValueError。那时候验证码已经解完、
    # token 已经拿到了,白烧一个。所以在这里就挡住,让调用方早点知道。
    if len(ticket) < MIN_TICKET_LEN:
        return None

    if now_ms is None:
        now_ms = int(time.time() * 1000)
    if user_agent is None:
        user_agent = rand_ua()
    if screen is None:
        screen = pick_screen(user_agent)

    key_meta = ticket[:16]
    ctr_meta = ticket[16:32]
    key_stream = ticket[1:17]
    ctr_stream = ticket[17:33]

    meta_plain = json.dumps({
        "browserInfo": [{
            "screen": screen,
            "ua": user_agent,
            "time": now_ms
        }]
    }, separators=(',', ':'))

    stream_plain = json.dumps({
        "events": [{"event": 1, "data": {"time": now_ms}}]
    }, separators=(',', ':'))

    meta = aes_ctr_encrypt(
        meta_plain,
        [ord(c) for c in key_meta],
        [ord(c) for c in ctr_meta]
    ).hex()

    stream = aes_ctr_encrypt(
        stream_plain,
        [ord(c) for c in key_stream],
        [ord(c) for c in ctr_stream]
    ).hex()

    return meta, stream


#获取ticket

def extract_ticket(arg):
    #从 auth URL 或原始 ticket 字符串取出 ticket。不读任何文件
    #
    # HTTP 接口一律用这个。外面传进来的东西不能拿去碰服务器上的文件 —— 以前这里看到
    # 含斜杠的输入就当路径去 open(),传 /etc/passwd 进来会把文件内容读出来当 ticket,
    # 然后 URL 编码后发到上游去。要从文件读的走 extract_ticket_from_arg。
    t = arg.strip()
    if t.startswith('http'):
        parsed = urllib.parse.urlparse(t)
        qs = urllib.parse.parse_qs(parsed.query)
        if 'd' in qs:
            return qs['d'][0]
        return t
    return t


def extract_ticket_from_arg(arg):
    #命令行专用：跟 extract_ticket 一样,但看着像路径时会当文件读
    #
    # 只给命令行参数用（python main.py tickets.txt 那种）。HTTP 接口绝对不能调这个,
    # 那等于让任何能访问接口的人指定服务器上的文件路径。
    t = arg.strip()
    if t.startswith('http'):
        return extract_ticket(t)
    if t.endswith('.txt') or '/' in t or '\\' in t:
        try:
            with open(t) as f:
                content = f.read().strip()
                if content:
                    return extract_ticket_from_arg(content)
        except (IOError, OSError):
            pass
    return t


def decode_callback_url(loot_url):
    # 从loot URL的r=参数解码回调URL
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(loot_url).query)
    r_param = qs.get('r', [''])[0]
    if not r_param:
        return None
    b64 = r_param.replace('-', '+').replace('_', '/')
    padding = (4 - len(b64) % 4) % 4
    try:
        dec = base64.b64decode(b64 + '=' * padding).decode('utf-8')
        if dec.startswith('http'):
            return dec
    except Exception:
        pass
    return None


def extract_ticket_from_callback(callback_url):
    # 从回调URL获取下一个ticket
    if not callback_url:
        return None
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(callback_url).query)
    return qs.get('d', [None])[0]


#步骤

#urllib3连接池
# 高并发：单主机连接池要够大，否则请求排队等连接（原 maxsize=1 是并发瓶颈）
step_pool = urllib3.PoolManager(
    num_pools=8, maxsize=64, block=False, retries=False,
    timeout=urllib3.Timeout(connect=3.0, read=8.0),
)

def create_session():
    #构建requests
    s = requests.Session()
    s.headers.update({
        'User-Agent': rand_ua(),
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
    })
    #无重试
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=8, pool_maxsize=32, max_retries=0)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    return s


def do_step(ticket, service=3, session=None, now_ms=None):
    # PUT /api/session/step
    #
    # 新版协议不校验 captcha 字段(可为 null),旧版图形验证码已随上游换 orbit 类型
    # 而作废,这里按真实浏览器抓包的形态发 null。
    step_ua = rand_ua()

    # ticket 太短就直接说不行,别往上游发。
    # 以前这里会让 AES 抛 ValueError,一路传到 main.py 的 except 才被接住,
    # 白跑一整轮。
    built = build_meta_stream(ticket, now_ms, user_agent=step_ua)
    if built is None:
        return {"success": False,
                "error": f"ticket 长度不足（{len(ticket)} 字符，至少要 {MIN_TICKET_LEN} 个）"}
    meta, stream = built

    url = f"{AUTH_API}/session/step?ticket={urllib.parse.quote(ticket)}&service={service}"

    body = json.dumps({
        "captcha": None,
        "meta": meta,
        "stream": stream,
        "resolved": True
    }).encode()

    STEP_HTTP_RETRIES = 3        
    STEP_RETRY_SLEEP = 0.5      
    last_err = None
    for attempt in range(STEP_HTTP_RETRIES + 1):
        try:
            r = step_pool.request('PUT', url, body=body, redirect=False, headers={
                'User-Agent': step_ua,
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/plain, */*',
                'x-client-name': 'platoboost webclient',
                'x-client-version': client_version()
            })
            if r.status != 200:
                last_err = f"http {r.status}"
                if attempt < STEP_HTTP_RETRIES:
                    time.sleep(STEP_RETRY_SLEEP)
                    continue
                return {"success": False, "error": last_err}
            try:
                return json.loads(r.data)
            except Exception:
                last_err = "non-json response"
                if attempt < STEP_HTTP_RETRIES:
                    time.sleep(STEP_RETRY_SLEEP)
                    continue
                return {"success": False, "error": last_err}
        except Exception as e:
            last_err = str(e)
            if attempt < STEP_HTTP_RETRIES:
                time.sleep(STEP_RETRY_SLEEP)
                continue
            return {"success": False, "error": last_err}
    return {"success": False, "error": last_err or "step failed"}


def get_json(path_qs, retries=3, sleep=0.25):
    last_err = None
    for attempt in range(retries + 1):
        try:
            r = step_pool.request('GET', f"{AUTH_API}/{path_qs}",
                redirect=False,
                headers={'User-Agent': rand_ua(), 'Accept': 'application/json'})
            if r.status != 200:
                last_err = f"http {r.status}"
                if attempt < retries:
                    time.sleep(sleep)
                    continue
                return {"success": False, "error": last_err, "transient": True}
            try:
                return json.loads(r.data)
            except Exception:
                last_err = "non-json response"
                if attempt < retries:
                    time.sleep(sleep)
                    continue
                return {"success": False, "error": last_err, "transient": True}
        except Exception as e:
            last_err = str(e)
            if attempt < retries:
                time.sleep(sleep)
                continue
            return {"success": False, "error": last_err, "transient": True}
    return {"success": False, "error": last_err or "get failed", "transient": True}


def get_session_status(ticket, session=None):
    # GET /api/session/status
    return get_json(f"session/status?ticket={urllib.parse.quote(ticket)}")


def get_session_metadata(ticket, session=None):
    # GET /api/session/metadata
    return get_json(f"session/metadata?ticket={urllib.parse.quote(ticket)}")


INVALID_MARKERS = ('invalid payload', 'expired', 'not found', 'invalid session',
                     'invalid ticket', 'does not exist')


def check_ticket_valid(ticket, session=None):
    try:
        meta = get_session_metadata(ticket, session=session)
    except Exception:
        return True, None
    if not isinstance(meta, dict):
        return True, None
    if meta.get('success') is True:
        return True, None
    if meta.get('transient'):
        return True, None
    if meta.get('success') is False:
        msg = str(meta.get('message') or meta.get('error') or '').lower()
        if any(m in msg for m in INVALID_MARKERS):
            return False, str(meta.get('message') or meta.get('error') or 'invalid link')
        return True, None
    return True, None