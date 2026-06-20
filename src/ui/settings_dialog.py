"""设置对话框 — 字体大小 + 界面缩放 + 源代码 + 开发日志."""

import os
import sys

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                              QLabel, QSpinBox, QPushButton,
                              QDialogButtonBox, QTextEdit)
from PyQt5.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, current_font_size=10, scale_pct=100, lang="zh", parent=None):
        super().__init__(parent)
        self._lang = lang
        self.setWindowTitle("设置" if lang == "zh" else "Settings")
        self.setFixedSize(310, 240)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 16)

        # 字体大小
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("字体大小" if lang == "zh" else "Font Size"))
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 24); self.font_spin.setValue(current_font_size)
        self.font_spin.setSuffix(" px"); self.font_spin.setFixedWidth(80)
        r1.addWidget(self.font_spin); r1.addStretch()
        layout.addLayout(r1)

        # 界面缩放
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("界面缩放" if lang == "zh" else "UI Scale"))
        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(70, 200); self.scale_spin.setValue(scale_pct)
        self.scale_spin.setSuffix(" %"); self.scale_spin.setSingleStep(10)
        self.scale_spin.setFixedWidth(90)
        r2.addWidget(self.scale_spin); r2.addStretch()
        layout.addLayout(r2)

        # 底部按钮行
        r3 = QHBoxLayout()
        self.source_btn = QPushButton("源代码" if lang == "zh" else "Source")
        self.source_btn.setProperty("cssClass", "secondary")
        self.source_btn.clicked.connect(self._show_source)
        r3.addWidget(self.source_btn)

        self.devlog_btn = QPushButton("开发日志" if lang == "zh" else "Dev Log")
        self.devlog_btn.setProperty("cssClass", "secondary")
        self.devlog_btn.clicked.connect(self._show_devlog)
        r3.addWidget(self.devlog_btn)
        r3.addStretch()
        layout.addLayout(r3)

        layout.addStretch()

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def font_size(self): return self.font_spin.value()
    def scale_pct(self): return self.scale_spin.value()

    def _show_source(self):
        from .i18n import T
        L = self._lang
        win = QDialog(self)
        win.setWindowTitle(T["source_title"][L])
        win.resize(640, 500)
        layout = QVBoxLayout(win)
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setFontFamily("Consolas, Microsoft YaHei, monospace")
        txt.setFontPointSize(9)

        content = T["mit_header"][L]
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for name in ["main.py", "gear/params.py", "gear/involute.py",
                     "catia/connector.py", "catia/gear_builder.py", "catia/naming.py",
                     "ui/gear_preview.py", "ui/main_window.py", "ui/settings_dialog.py",
                     "ui/widgets.py", "ui/styles.py", "ui/i18n.py"]:
            content += f"\n{'='*60}\n# {name}\n{'='*60}\n"
            try:
                with open(os.path.join(base, *name.split("/")), "r", encoding="utf-8") as f:
                    content += f.read()
            except Exception:
                content += f"# {name} not available\n"
        txt.setPlainText(content)
        layout.addWidget(txt)
        close_btn = QPushButton("OK")
        close_btn.clicked.connect(win.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        win.exec_()

    def _show_devlog(self):
        from .i18n import T
        L = self._lang
        win = QDialog(self)
        win.setWindowTitle(T["devlog_title"][L])
        win.resize(500, 520)
        layout = QVBoxLayout(win)
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setFontFamily("Microsoft YaHei, Segoe UI, sans-serif")
        txt.setFontPointSize(10)
        txt.setPlainText(T["devlog_content"][L])
        layout.addWidget(txt)
        close_btn = QPushButton("OK")
        close_btn.clicked.connect(win.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        win.exec_()
