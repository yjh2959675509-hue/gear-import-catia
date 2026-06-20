"""PyInstaller 构建脚本 — 生成 齿轮一键导入.exe"""

import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
ICON = os.path.join(SRC, "resources", "icon.ico")
MAIN = os.path.join(SRC, "main.py")
DIST = ROOT
DESKTOP = os.path.expanduser(r"~\Desktop")
OUTPUT_NAME = "齿轮一键导入"

# PyInstaller 参数
pyi = os.path.join(os.path.dirname(sys.executable), "Scripts", "pyinstaller.exe")
cmd = [
    pyi,
    "--name", OUTPUT_NAME,
    "--onefile",
    "--windowed",           # 不显示控制台窗口
    "--clean",
    "--noconfirm",
    f"--distpath={DIST}",
    f"--workpath={os.path.join(ROOT, 'build_temp')}",
    f"--specpath={ROOT}",
    "--add-data", f"{ICON}{os.pathsep}resources",
    "--hidden-import", "win32com",
    "--hidden-import", "win32com.client",
    "--hidden-import", "pythoncom",
    "--hidden-import", "PyQt5.sip",
    "--hidden-import", "OpenGL",
    "--hidden-import", "OpenGL.GL",
    "--hidden-import", "OpenGL.GLU",
    MAIN,
]

if os.path.exists(ICON):
    cmd.insert(4, f"--icon={ICON}")

print(f"Building {OUTPUT_NAME}.exe ...")
print(f"  Source: {MAIN}")
print(f"  Icon:   {ICON}")
print(f"  Dist:   {DIST}")

result = subprocess.run(cmd, cwd=ROOT)

if result.returncode == 0:
    exe_src = os.path.join(DIST, f"{OUTPUT_NAME}.exe")
    exe_dst = os.path.join(DESKTOP, f"{OUTPUT_NAME}.exe")
    try:
        import shutil
        shutil.copy2(exe_src, exe_dst)
        print(f"\nCopied to Desktop: {exe_dst}")
    except Exception as e:
        print(f"\nBuild OK but copy to Desktop failed: {e}")
        print(f"  .exe is at: {exe_src}")
else:
    print(f"\nBuild FAILED (exit code {result.returncode})")
    sys.exit(result.returncode)
