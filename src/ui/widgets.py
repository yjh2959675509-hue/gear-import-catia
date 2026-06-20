"""自定义控件。"""

from PyQt5.QtWidgets import (QLineEdit, QWidget, QHBoxLayout, QVBoxLayout,
                              QLabel, QPushButton, QFileDialog, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator


class _UnitInput(QFrame):
    """带固定单位后缀的输入框 — QLineEdit + QLabel 内嵌."""

    valueChanged = pyqtSignal()
    textChanged = pyqtSignal(str)

    def __init__(self, default_value: str, unit: str = "",
                 is_int: bool = False, min_val: float = 0.01, max_val: float = 9999.0):
        super().__init__()
        self._unit = unit

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.edit = QLineEdit(str(default_value))
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setFrame(False)
        if is_int:
            self.edit.setValidator(QIntValidator(int(min_val), int(max_val)))
        else:
            self.edit.setValidator(QDoubleValidator(min_val, max_val, 2))

        self.unit_lbl = QLabel(f" {unit} ") if unit else QLabel("")
        self.unit_lbl.setStyleSheet("color: #616161; background: transparent; padding-right: 4px;")

        layout.addWidget(self.edit, 1)
        if unit:
            layout.addWidget(self.unit_lbl)

        self.setStyleSheet("""
            _UnitInput {
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                background: #FAFAFA;
                padding: 2px;
            }
            _UnitInput:focus-within {
                border: 2px solid #0078D4;
                padding: 1px;
            }
        """)

        self.edit.returnPressed.connect(self.valueChanged.emit)
        self.edit.editingFinished.connect(self.valueChanged.emit)
        self.edit.textChanged.connect(self.textChanged.emit)

    def text(self) -> str:
        return self.edit.text()

    def setText(self, v: str):
        self.edit.setText(v)

    def set_error(self, active: bool):
        if active:
            self.setStyleSheet("""
                _UnitInput { border: 2px solid #D13438; border-radius: 4px;
                background: #FAFAFA; padding: 1px; }
                _UnitInput:focus-within { border: 2px solid #D13438; padding: 1px; }
            """)
        else:
            self.setStyleSheet("""
                _UnitInput { border: 1px solid #D0D0D0; border-radius: 4px;
                background: #FAFAFA; padding: 2px; }
                _UnitInput:focus-within { border: 2px solid #0078D4; padding: 1px; }
            """)


class ParamInput(QWidget):
    """参数输入行: [标签] [输入框|单位]"""

    valueChanged = pyqtSignal(float)
    textChanged = pyqtSignal(str)

    def __init__(self, label: str, default_value: str,
                 unit: str = "", is_int: bool = False,
                 min_val: float = 0.01, max_val: float = 9999.0,
                 label_w: int = 60, edit_w: int = 95):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 1, 0, 1)
        layout.setSpacing(6)

        self.lbl = QLabel(label)
        self.lbl.setProperty("cssClass", "param")
        self.lbl.setFixedWidth(label_w)

        self.input = _UnitInput(default_value, unit, is_int, min_val, max_val)
        self.input.setFixedWidth(edit_w)
        self.input.valueChanged.connect(self._emit_value)
        self.input.textChanged.connect(self.textChanged.emit)

        layout.addWidget(self.lbl)
        layout.addWidget(self.input)
        layout.addStretch()

    def _emit_value(self):
        text = self.input.text().strip()
        if not text:
            self.input.set_error(True)
            return
        self.input.set_error(False)
        try:
            v = float(text)
            self.valueChanged.emit(v)
        except ValueError:
            self.input.set_error(True)

    def value(self) -> float:
        try:
            return float(self.input.text().strip())
        except ValueError:
            return 0.0

    def set_value(self, v):
        self.input.setText(str(v))

    def set_error(self, msg: str = ""):
        self.input.set_error(bool(msg))


class ComputedDisplay(QWidget):
    """自动计算显示行: [标签] [数值 单位]"""

    def __init__(self, label: str, label_w: int = 60, val_w: int = 95):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 1, 0, 1)
        layout.setSpacing(6)

        self.lbl = QLabel(label)
        self.lbl.setProperty("cssClass", "param")
        self.lbl.setFixedWidth(label_w)

        self.val_lbl = QLabel("--")
        self.val_lbl.setProperty("cssClass", "computed")
        self.val_lbl.setFixedWidth(val_w)
        self.val_lbl.setAlignment(Qt.AlignRight)

        layout.addWidget(self.lbl)
        layout.addWidget(self.val_lbl)
        layout.addStretch()

    def set_value(self, v: float):
        self.val_lbl.setText(f"{v:.2f} mm")


class FilePicker(QWidget):
    """文件选择器: [路径显示] [浏览按钮]"""

    fileSelected = pyqtSignal(str)

    def __init__(self, filter_str: str = "CATPart 文件 (*.CATPart)"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择目标 .CATPart 文件...")
        self.path_edit.setReadOnly(True)

        self.browse_btn = QPushButton("浏览")
        self.browse_btn.setProperty("cssClass", "secondary")
        self.browse_btn.setFixedWidth(55)
        self.browse_btn.clicked.connect(self._browse)

        layout.addWidget(self.path_edit, 1)
        layout.addWidget(self.browse_btn)

        self._filter = filter_str

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择目标 CATPart 文件", "",
            self._filter)
        if path:
            self.path_edit.setText(path)
            self.fileSelected.emit(path)

    def path(self) -> str:
        return self.path_edit.text().strip()

    def setPlaceholder(self, text: str):
        self.path_edit.setPlaceholderText(text)

    def set_path(self, p: str):
        self.path_edit.setText(p)
