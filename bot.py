    if "http://" in user_text or "https://" in user_text:
        wait_msg = "⏳ جارٍ معالجة الرابط واستخراج النتيجة، انتظر قليلاً..."
        status_msg = await update.message.reply_text(wait_msg)
        
        start_time = asyncio.get_event_loop().time()
        extracted_result = ""
        
        try:
            loop = asyncio.get_running_loop()
            if "platorelay.com" in user_text or "delta" in user_text.lower():
                # تشغيل main.py مع الرابط تماماً كما يعمل بالأداة الأساسية
                process = await asyncio.create_subprocess_exec(
                    "python", "main.py", user_text,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                output_text = stdout.decode('utf-8', errors='ignore').strip()
                
                # استخراج النتيجة من المخرجات
                for line in output_text.splitlines():
                    if "http://" in line or "https://" in line or "FREE_" in line or "key" in line.lower():
                        if user_text not in line and "127.0.0.1" not in line:
                            extracted_result = line.strip()
                            break
                if not extracted_result:
                    extracted_result = output_text
            else:
                if bypass_link_func:
                    res = await loop.run_in_executor(None, bypass_link_func, user_text)
                    if hasattr(res, "value") and res.value:
                        extracted_result = str(res.value)
                    elif hasattr(res, "url") and res.url:
                        extracted_result = str(res.url)
                    elif hasattr(res, "result") and res.result:
                        extracted_result = str(res.result)
                    else:
                        extracted_result = str(res)
                else:
                    extracted_result = "Linkvertise module not loaded."
        except Exception as ex:
            extracted_result = str(ex)

        elapsed_time = asyncio.get_event_loop().time() - start_time
        
        try:
            await status_msg.delete()
        except:
            pass

        res_lower = extracted_result.lower()
        if extracted_result and "traceback" not in res_lower and len(extracted_result) > 5:
            successful_requests_count += 1
            save_data()
            
            result_message = (
                f"✅ **تم تجاوز الرابط بنجاح:**\n\n"
                f"`{extracted_result}`\n\n"
                f"⏳ الوقت المستغرق: {elapsed_time:.2f} ثانية"
            )
            await update.message.reply_text(result_message, parse_mode="Markdown", reply_markup=get_main_keyboard())
        else:
            fail_message = f"❌ فشل في تجاوز الرابط!\n\n`{extracted_result}`"
            await update.message.reply_text(fail_message, parse_mode="Markdown", reply_markup=get_main_keyboard())
