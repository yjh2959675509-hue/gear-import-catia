"""Win11 风格 QSS 样式表."""

FONT_FAMILY = "Microsoft YaHei"
ACCENT = "#0078D4"
ACCENT_HOVER = "#1A88E0"
ACCENT_PRESS = "#006CBE"
SURFACE = "#F3F3F3"
BG = "#FFFFFF"
FG = "#1A1A1A"
FG_SECONDARY = "#616161"
BORDER = "#D0D0D0"
RADIUS = "4px"

_DEFAULT_FONT_SIZE = 10

STYLESHEET = f"""
QWidget {{
    font-family: "{FONT_FAMILY}";
    font-size: __FONT_SIZE__px;
    font-weight: bold;
    color: {FG};
    background-color: {SURFACE};
}}

QMainWindow {{
    background-color: {SURFACE};
}}

QLineEdit {{
    background-color: {BG};
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
    padding: 3px 6px;
    min-height: 14px;
    selection-background-color: {ACCENT};
    selection-color: white;
    font-weight: bold;
}}
QLineEdit:focus {{
    border: 1px solid {ACCENT};
}}
QLineEdit:disabled {{
    background-color: #F0F0F0;
    color: #999;
}}

QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: {RADIUS};
    padding: 5px 16px;
    font-weight: bold;
    min-height: 16px;
}}
QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton:pressed {{
    background-color: {ACCENT_PRESS};
}}
QPushButton:disabled {{
    background-color: #CCC;
    color: #888;
}}

QPushButton[cssClass="secondary"] {{
    background-color: {BG};
    color: {FG};
    border: 1px solid {BORDER};
}}
QPushButton[cssClass="secondary"]:hover {{
    background-color: #F0F0F0;
}}

QPushButton[cssClass="preview"] {{
    background-color: transparent;
    color: {ACCENT};
    border: 1px solid {BORDER};
    border-radius: 3px;
    padding: 0;
    font-size: __FONT_SIZE_M1__px;
}}
QPushButton[cssClass="preview"]:hover {{
    background-color: #E8F4FD;
    border-color: {ACCENT};
}}

QPushButton[cssClass="settings"] {{
    background-color: transparent;
    color: {FG_SECONDARY};
    border: 1px solid transparent;
    border-radius: {RADIUS};
    padding: 2px 6px;
}}
QPushButton[cssClass="settings"]:hover {{
    background-color: #E8E8E8;
    border-color: {BORDER};
}}

QLabel[cssClass="title"] {{
    font-size: __FONT_SIZE_P2__px;
    font-weight: bold;
}}
QLabel[cssClass="param"] {{
    font-weight: bold;
}}
QLabel[cssClass="computed"] {{
    color: {ACCENT};
    font-weight: bold;
}}
QLabel[cssClass="status"] {{
    font-size: __FONT_SIZE_M1__px;
    color: {FG_SECONDARY};
    font-weight: normal;
}}

QGroupBox {{
    background-color: {BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 8px;
    padding: 10px 8px 6px 8px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}

QMessageBox {{
    background-color: {BG};
}}
QMessageBox QLabel {{
    color: {FG};
    font-size: __FONT_SIZE__px;
    min-width: 180px;
}}
QMessageBox QPushButton {{
    padding: 5px 20px;
    min-width: 70px;
}}

QDialog {{
    background-color: {BG};
}}

QScrollBar:vertical {{
    width: 6px;
    background: transparent;
}}
QScrollBar::handle:vertical {{
    background: #C0C0C0;
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: #A0A0A0;
}}
"""


def get_stylesheet(font_size: int = None) -> str:
    s = font_size or _DEFAULT_FONT_SIZE
    return (STYLESHEET
            .replace("__FONT_SIZE_P2__", str(s + 2))
            .replace("__FONT_SIZE_M1__", str(s - 1))
            .replace("__FONT_SIZE__", str(s)))
