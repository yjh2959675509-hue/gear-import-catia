"""齿轮一键导入 CATIA — 入口点."""

import sys
import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QSurfaceFormat


def main():
    # MSAA 多重采样 (4x) — 必须在 QApplication 创建前设置
    fmt = QSurfaceFormat()
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)

    # 高 DPI 支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    if hasattr(Qt, 'AA_DisableWindowContextHelpButton'):
        QApplication.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)

    app = QApplication(sys.argv)
    app.setApplicationName("齿轮一键导入")

    icon_path = os.path.join(SRC_DIR, "resources", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
