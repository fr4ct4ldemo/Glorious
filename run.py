import subprocess
import sys
import os

print("=" * 50)
print("   ⚡ GLORIOUS BOT + DASHBOARD LAUNCHER")
print("=" * 50)

bot_process = subprocess.Popen(
    [sys.executable, "glorious.py"],
    cwd=os.path.dirname(os.path.abspath(__file__))
)

dashboard_process = subprocess.Popen(
    ["node", "server.js"],
    cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard")
)

print("[+] Glorious bot is now running!")
print("[+] Dashboard is running at http://localhost:3000")
print("=" * 50)
print("Press CTRL+C to stop both")
print("=" * 50)

try:
    bot_process.wait()
    dashboard_process.wait()
except KeyboardInterrupt:
    print("\n[-] Shutting down...")
    bot_process.terminate()
    dashboard_process.terminate()
    bot_process.wait()
    dashboard_process.wait()
    print("[+] Both stopped successfully!")
