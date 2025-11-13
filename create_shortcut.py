"""
Создать ярлык (.lnk) на рабочем столе.

Примеры:
  python create_shortcut.py
  python create_shortcut.py --name "MyGame.lnk" --target pythonw
  python create_shortcut.py --target run-bat --force

Автоустановка:
  При отсутствии win32com (pywin32) скрипт попытается выполнить:
    python -m pip install pywin32
  и затем импортировать win32com. Если установка неуспешна — используется VBS-фоллбек.
"""

import os
import sys
import shutil
import tempfile
import subprocess
import argparse

def get_desktop_path(custom=None):
    if custom:
        return os.path.expanduser(custom)
    home = os.path.expanduser("~")
    desktop = os.path.join(home, "Desktop")
    return desktop

def ensure_pywin32():
    try:
        import win32com  # type: ignore
        return True
    except Exception:
        pass
    # Пытаться установить pywin32 в текущем интерпретаторе
    try:
        print("pywin32 не найден — пытаюсь установить через pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
    except Exception as e:
        print("Ошибка установки pywin32:", e, file=sys.stderr)
        return False
    # Попробовать импортировать снова
    try:
        import win32com  # type: ignore
        return True
    except Exception as e:
        print("После установки импорт win32com не удался:", e, file=sys.stderr)
        return False

def create_shortcut_win32(shortcut_path, target, args="", workdir=None, icon=None, description=""):
    from win32com.client import Dispatch  # type: ignore
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target
    if args:
        shortcut.Arguments = args
    if workdir:
        shortcut.WorkingDirectory = workdir
    if icon:
        shortcut.IconLocation = icon
    if description:
        shortcut.Description = description
    shortcut.save()

def create_shortcut_vbs(shortcut_path, target, args="", workdir=None, icon=None, description=""):
    vbs = []
    vbs.append('Set oWS = WScript.CreateObject("WScript.Shell")')
    vbs.append('Set oLink = oWS.CreateShortcut("{}")'.format(shortcut_path.replace('"', '""')))
    vbs.append('oLink.TargetPath = "{}"'.format(target.replace('"', '""')))
    if args:
        vbs.append('oLink.Arguments = "{}"'.format(args.replace('"', '""')))
    if workdir:
        vbs.append('oLink.WorkingDirectory = "{}"'.format(workdir.replace('"', '""')))
    if icon:
        vbs.append('oLink.IconLocation = "{}"'.format(icon.replace('"', '""')))
    if description:
        vbs.append('oLink.Description = "{}"'.format(description.replace('"', '""')))
    vbs.append('oLink.Save')

    fd, path = tempfile.mkstemp(suffix=".vbs", text=True)
    os.close(fd)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(vbs))
        subprocess.check_call(["cscript", "//NoLogo", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

def parse_args():
    p = argparse.ArgumentParser(description="Create desktop shortcut for pythonGame")
    p.add_argument("--name", "-n", default="pythonGame.lnk", help="Имя ярлыка (по умолчанию: pythonGame.lnk)")
    p.add_argument("--target", "-t", choices=["pythonw", "python", "run-bat"], default="pythonw",
                   help="Что запускать: pythonw|python|run-bat (run_game.bat в проекте)")
    p.add_argument("--script", "-s", default=None, help="Путь к main.py (по умолчанию — ./main.py в проекте)")
    p.add_argument("--desktop", "-d", default=None, help="Путь к рабочему столу (по умолчанию определяется автоматически)")
    p.add_argument("--icon", help="Путь к файлу иконки (.ico) для ярлыка")
    p.add_argument("--force", "-f", action="store_true", help="Перезаписать существующий ярлык")
    return p.parse_args()

def main():
    args = parse_args()
    project_dir = os.path.dirname(os.path.abspath(__file__))
    desktop = get_desktop_path(args.desktop)
    os.makedirs(desktop, exist_ok=True)
    shortcut_path = os.path.join(desktop, args.name)

    # выбрать цель запуска
    run_bat = os.path.join(project_dir, "run_game.bat")
    if args.target == "run-bat":
        if not os.path.exists(run_bat):
            print("run_game.bat не найден в проекте, создайте run_game.bat или выберите другую цель.", file=sys.stderr)
            sys.exit(1)
        target = run_bat
        target_args = ""
    else:
        pythonw_path = shutil.which("pythonw")
        python_path = shutil.which("python")
        if args.target == "pythonw":
            if pythonw_path:
                target = pythonw_path
            elif python_path:
                print("pythonw не найден, падаем на python")
                target = python_path
            else:
                print("Не найден python/pythonw в PATH.", file=sys.stderr)
                sys.exit(1)
        else:  # "python"
            if python_path:
                target = python_path
            elif pythonw_path:
                target = pythonw_path
            else:
                print("Не найден python в PATH.", file=sys.stderr)
                sys.exit(1)
        # скрипт для передачи как аргумент
        script_path = args.script or os.path.join(project_dir, "main.py")
        if not os.path.exists(script_path):
            print("Не найден скрипт для запуска:", script_path, file=sys.stderr)
            sys.exit(1)
        target_args = '"{}"'.format(script_path)

    if os.path.exists(shortcut_path) and not args.force:
        print("Ярлык уже существует:", shortcut_path, "(используйте --force для перезаписи)")
        return

    workdir = project_dir
    description = "Запуск pythonGame"
    icon = args.icon

    # Попытка создать через win32 (pywin32). Если не установлен — попытка автoустановки.
    use_win32 = ensure_pywin32()
    if use_win32:
        try:
            create_shortcut_win32(shortcut_path, target, args=target_args, workdir=workdir, icon=icon, description=description)
            print("Ярлык создан (win32):", shortcut_path)
            return
        except Exception as e:
            print("Ошибка создания ярлыка через win32com:", e, file=sys.stderr)

    # fallback на VBS
    try:
        create_shortcut_vbs(shortcut_path, target, args=target_args, workdir=workdir, icon=icon, description=description)
        print("Ярлык создан (VBS):", shortcut_path)
    except Exception as e:
        print("Не удалось создать ярлык:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
