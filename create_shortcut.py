r"""
Создать ярлык .lnk, который запускает pythonw с аргументом (main.py).
Автоустановка pywin32 по умолчанию; можно отключить --no-install.
Примеры:
  python create_shortcut.py
  python create_shortcut.py --name "MyGame.lnk" --force
  python create_shortcut.py --script "C:\path\to\main.py" --icon "C:\icon.ico"
"""
import os
import sys
import shutil
import subprocess
import tempfile
import argparse

def get_desktop_path(custom=None):
    # возвращение пути к рабочему столу пользователя
    if custom:
        return os.path.expanduser(custom)
    home = os.path.expanduser("~")
    return os.path.join(home, "Desktop")

def try_install_pywin32(timeout=120):
    """Попытаться установить pywin32 в текущем интерпретаторе.
    Возвращает True при успехе, False при неудаче или при истечении таймаута.
    Использует --user, чтобы обычно избежать прав администратора.
    """
    cmd = [sys.executable, "-m", "pip", "install", "--user", "pywin32", "--disable-pip-version-check"]
    try:
        print("Пытаюсь установить pywin32: {}".format(" ".join(cmd)))
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
        return True
    except subprocess.CalledProcessError as e:
        print("pip вернул ошибку при установке pywin32:", e, file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("Установка pywin32 превысила время ожидания ({}s).".format(timeout), file=sys.stderr)
        return False
    except KeyboardInterrupt:
        print("Установка прервана пользователем.", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("pip не найден (вызов python -m pip завершился некорректно).", file=sys.stderr)
        return False
    except Exception as e:
        print("Неожиданная ошибка при попытке установки pywin32:", e, file=sys.stderr)
        return False

def ensure_win32(no_install=False):
    """Попытаться импортировать win32com; при отсутствии и разрешении — установить pywin32."""
    try:
        import win32com  # type: ignore
        return True
    except Exception:
        pass

    if no_install:
        print("win32com не найден и автоустановка отключена (--no-install). Используем VBS-фоллбек.")
        return False

    ok = try_install_pywin32()
    if not ok:
        print("Автоустановка pywin32 не удалась — используем VBS-фоллбек.", file=sys.stderr)
        return False

    # попытка импортировать после установки
    try:
        import importlib
        importlib.invalidate_caches()
        import win32com  # type: ignore
        return True
    except Exception as e:
        print("После установки импорт win32com не удался:", e, file=sys.stderr)
        return False

# Создание ярлыка через win32com
def create_shortcut_win32(path, target, args="", workdir=None, icon=None, desc=""):
    from win32com.client import Dispatch  # type: ignore
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.Arguments = args or ""
    if workdir:
        shortcut.WorkingDirectory = workdir
    if icon:
        shortcut.IconLocation = icon
    if desc:
        shortcut.Description = desc
    shortcut.save()

# Создание ярлыка через VBS
def create_shortcut_vbs(path, target, args="", workdir=None, icon=None, desc=""):
    vbs = [
        'Set oWS = WScript.CreateObject("WScript.Shell")',
        'Set oLink = oWS.CreateShortcut("{}")'.format(path.replace('"','""')),
        'oLink.TargetPath = "{}"'.format(target.replace('"','""'))
    ]
    if args:
        vbs.append('oLink.Arguments = "{}"'.format(args.replace('"','""')))
    if workdir:
        vbs.append('oLink.WorkingDirectory = "{}"'.format(workdir.replace('"','""')))
    if icon:
        vbs.append('oLink.IconLocation = "{}"'.format(icon.replace('"','""')))
    if desc:
        vbs.append('oLink.Description = "{}"'.format(desc.replace('"','""')))
    vbs.append('oLink.Save')

    fd, tmp = tempfile.mkstemp(suffix=".vbs", text=True)
    os.close(fd)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("\n".join(vbs))
        # запуск cscript для выполнения скрипта создания ярлыка (без вывода)
        subprocess.check_call(["cscript", "//NoLogo", tmp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    except subprocess.TimeoutExpired:
        print("VBS-скрипт создания ярлыка превысил время ожидания.", file=sys.stderr)
        raise
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass

# Парсинг аргументов командной строки
def parse_args():
    p = argparse.ArgumentParser(description="Create a pythonw shortcut for this project")
    p.add_argument("--name", "-n", default="pythonGame.lnk", help="Shortcut name on desktop")
    p.add_argument("--script", "-s", default=None, help="Path to script to pass as argument (default: ./main.py)")
    p.add_argument("--icon", help="Path to .ico file for the shortcut")
    p.add_argument("--desktop", help="Custom desktop folder (default: current user's Desktop)")
    p.add_argument("--force", "-f", action="store_true", help="Overwrite existing shortcut")
    p.add_argument("--no-install", action="store_true", help="Do not attempt to install pywin32 automatically")
    return p.parse_args()

# Главная функция
def main():
    args = parse_args()
    project_dir = os.path.dirname(os.path.abspath(__file__))
    desktop = get_desktop_path(args.desktop)
    os.makedirs(desktop, exist_ok=True)
    shortcut_path = os.path.join(desktop, args.name)

    script = args.script or os.path.join(project_dir, "main.py")
    if not os.path.exists(script):
        print("Ошибка: не найден скрипт:", script, file=sys.stderr)
        sys.exit(1)

    # выбрать pythonw (без консоли) или python если pythonw отсутствует
    pythonw = shutil.which("pythonw")
    pythonexe = shutil.which("python")
    if pythonw:
        target = pythonw
    elif pythonexe:
        target = pythonexe
    else:
        print("Ошибка: python не найден в PATH", file=sys.stderr)
        sys.exit(1)

    target_args = '"{}"'.format(os.path.abspath(script))
    workdir = project_dir
    icon = args.icon
    desc = "Запуск pythonGame (pythonw)"

    if os.path.exists(shortcut_path) and not args.force:
        print("Ярлык уже существует:", shortcut_path, "(используйте --force для перезаписи)")
        return

    # попытка через win32com (pywin32)
    use_win32 = ensure_win32(no_install=args.no_install)
    if use_win32:
        try:
            create_shortcut_win32(shortcut_path, target, args=target_args, workdir=workdir, icon=icon, desc=desc)
            print("Ярлык создан (win32):", shortcut_path)
            return
        except Exception as e:
            print("Не удалось создать ярлык через win32com:", e, file=sys.stderr)

    # fallback через VBS (также создаёт .lnk, использует target = pythonw/python)
    try:
        create_shortcut_vbs(shortcut_path, target, args=target_args, workdir=workdir, icon=icon, desc=desc)
        print("Ярлык создан (VBS):", shortcut_path)
    except Exception as e:
        print("Ошибка: не удалось создать ярлык через VBS:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
