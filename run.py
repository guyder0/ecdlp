import argparse

parser = argparse.ArgumentParser(description="Запуск программы по решению ECDLP")
parser.add_argument('-p', '--port', type=int, help="Выбрать порт, на котором будет запущена программа", default=8000)
port = parser.parse_args().port

import sys
import subprocess
import threading
import time
import webbrowser
import re
from pathlib import Path
from importlib import metadata

# Конфигурация
REQUIRED_NODE_MAJOR = 24
BASE_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"


def check_python_deps():
    """Проверяет наличие библиотек из backend/requirements.txt."""
    req_file = BACKEND_DIR / "requirements.txt"
    if not req_file.exists():
        print("⚠️  Файл backend/requirements.txt не найден, пропускаю проверку Python-зависимостей.")
        return

    print("🔍 Проверка Python-зависимостей...")
    missing = []
    with open(req_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Извлекаем имя пакета (удаляем версии типа ==1.2.3)
            pkg_name = re.split(r'[<>=!]', line)[0].strip().replace("-", "_")
            
            try:
                metadata.version(pkg_name)
            except metadata.PackageNotFoundError:
                missing.append(line)

    if missing:
        print(f"❌ Отсутствуют библиотеки: {', '.join(missing)}")
        choice = input("👉 Установить их сейчас? (y/n): ").lower()
        if choice == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=True)
        else:
            print("❌ Запуск невозможен без зависимостей.")
            sys.exit(1)
    else:
        print("✅ Python-зависимости в порядке.")

def check_node_environment():
    """Проверяет Node.js и наличие node_modules."""
    print("🔍 Проверка Node.js среды...")
    
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        version_str = result.stdout.strip() # "v24.1.0"
        major_version = int(re.search(r'v(\d+)', version_str).group(1))
        
        if major_version < REQUIRED_NODE_MAJOR:
            print(f"❌ Ваша версия Node.js ({version_str}) слишком старая. Требуется v{REQUIRED_NODE_MAJOR}+")
            sys.exit(1)
        print(f"✅ Node.js {version_str} найдена.")
    except (subprocess.CalledProcessError, FileNotFoundError, AttributeError):
        print("❌ Node.js не найдена. Установите Node.js 24 или выше.")
        sys.exit(1)

    # 2. Проверка node_modules
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("⚠️  Папка node_modules не найдена. Устанавливаю зависимости фронтенда...")
        choice = input("👉 Установить зависимости сейчас? (y/n): ").lower()
        if choice == 'y':
            subprocess.run("npm install", cwd=FRONTEND_DIR, shell=True, check=True)
            print("✅ npm install завершен.")
        else:
            sys.exit(1)
    else:
        print("✅ Библиотеки Node.js установлены.")

def check_frontend_build():
    dist_path = FRONTEND_DIR / "dist"
    if not dist_path.exists() or not (dist_path / "index.html").exists():
        print("⚠️  Сборка фронтенда не найдена.")
        choice = input("👉 Собрать фронтенд сейчас? (y/n): ").lower()
        if choice == 'y':
            subprocess.run("npm run build", cwd=FRONTEND_DIR, shell=True, check=True)
        else:
            sys.exit(1)

def open_browser(port):
    time.sleep(1.5)
    webbrowser.open(f"http://127.0.0.1:{port}")

def start():
    # Запускаем все проверки
    check_python_deps()
    check_node_environment()
    check_frontend_build()
    
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "api.main:app",
        "--app-dir", str(BACKEND_DIR), 
        "--host", "127.0.0.1", 
        "--port", str(port),
        "--log-level", "info"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Выход...")

if __name__ == "__main__":
    start()