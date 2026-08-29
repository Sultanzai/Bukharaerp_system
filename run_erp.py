import os
import subprocess
import time
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

subprocess.Popen([
    r"E:\Self studies\Web Development 2026\ERP System\erp_system\venv\Scripts\python.exe",
    "manage.py",
    "runserver",
    "127.0.0.1:8000"
])

time.sleep(5)

webbrowser.open("http://127.0.0.1:8000")

input("Press Enter to exit...")