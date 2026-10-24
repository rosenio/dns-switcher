import subprocess
import sys
import os
from pathlib import Path

def get_silent_startupinfo():
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
        return startupinfo
    return None

def run_build():
    root_dir = Path(__file__).parent.parent.parent
    
    src_folder_name = "scr" if (root_dir / "scr").exists() else "src"
    entry_point = root_dir / src_folder_name / "dns_switcher" / "__init__.py"
    images_dir = root_dir / "images"
    app_icon = images_dir / "app_icon.ico"

    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--uac-admin",
        "--name=dns-switcher",
        f"--add-data={str(images_dir)}{os.pathsep}images",
        f"--icon={str(app_icon)}",
        str(entry_point)
    ]
    
    
    result = subprocess.run(cmd, startupinfo=get_silent_startupinfo())
    sys.exit(result.returncode)
