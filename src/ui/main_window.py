"""主窗口 — 齿轮参数输入 + CATIA 目标选择 + 导入 + 3D 预览."""

import os
import json
import traceback
import datetime
import threading

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QGroupBox, QMessageBox,
                              QFileDialog, QLineEdit, QSplitter, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from catia.connector import (CatiaConnector, get_connector,
                              load_config, save_config)
from catia.gear_builder import GearBuilder
from gear.params import GearParams
from .widgets import ParamInput, ComputedDisplay, FilePicker
from .settings_dialog import SettingsDialog
from .styles import get_stylesheet
from .gear_preview import GearPreviewWidget
from .i18n import _

LOG_FILE = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                         "齿轮一键导入", "debug.log")
try:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
except Exception:
    pass

DEFAULT_FONT_SIZE = 10
DEFAULT_SCALE_PCT = 100


def _log(msg: str):
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


class MainWindow(QMainWindow):

    _show_info = pyqtSignal(str, str)
    _show_error = pyqtSignal(str, str)
    _set_status = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("齿轮一键导入 CATIA")

        cfg = load_config()
        self._font_size = int(cfg.get("font_size", DEFAULT_FONT_SIZE))
        self._scale_pct = int(cfg.get("scale_pct", DEFAULT_SCALE_PCT))
        self._lang = cfg.get("lang", "zh")
        self._catia_ready = False
        self._connector = get_connector()
        self._preview_open = False

        self.setMinimumSize(330, 430)
        w, h = self._scaled(340, 470)
        self.resize(w, h)

        self._show_info.connect(self._on_show_info)
        self._show_error.connect(self._on_show_error)
        self._set_status.connect(self._on_set_status)

        # 预览防抖定时器: 200ms 内无新输入才重建网格
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(200)
        self._preview_timer.timeout.connect(self._update_preview)

        _log("=== 应用启动 ===")
        self._setup_ui()
        self._apply_style()
        QTimer.singleShot(200, self._check_catia_cache)

    def _scaled(self, w, h=None):
        f = self._scale_pct / 100.0
        if h is None:
            return int(w * f)
        return int(w * f), int(h * f)

    # ── UI ────────────────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ═══ 左面板 ═══
        left = QWidget()
        left.setFixedWidth(self._scaled(320))
        ml = QVBoxLayout(left)
        ml.setContentsMargins(10, 8, 6, 12)
        ml.setSpacing(5)

        # 顶部
        top = QHBoxLayout()
        title = QLabel(_("header", self._lang))
        title.setProperty("cssClass", "title")
        top.addWidget(title)
        top.addStretch()
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setProperty("cssClass", "settings")
        self.settings_btn.setFixedSize(34, 34)
        self.settings_btn.setToolTip("设置")
        self.settings_btn.clicked.connect(self._open_settings)
        top.addWidget(self.settings_btn)

        self.lang_btn = QPushButton(_("lang_btn", self._lang))
        self.lang_btn.setProperty("cssClass", "settings")
        self.lang_btn.setFixedSize(34, 34)
        self.lang_btn.setToolTip(_("lang_tip", self._lang))
        self.lang_btn.clicked.connect(self._toggle_lang)
        top.addWidget(self.lang_btn)
        ml.addLayout(top)

        # Part 1: 参数
        self.param_group = QGroupBox(_("sec_params", self._lang))
        pl = QVBoxLayout(self.param_group)
        pl.setSpacing(2)
        lw, ew = self._scaled(60), self._scaled(100)

        self.input_m   = ParamInput(_("label_m",self._lang), "4", _("unit_mm",self._lang), True, 0.5, 100, lw, ew)
        self.input_z   = ParamInput(_("label_z",self._lang), "20", "", True, 5, 500, lw, ew)
        self.display_d = ComputedDisplay(_("label_d",self._lang), lw, ew)
        self.input_alpha = ParamInput(_("label_alpha",self._lang), "20", _("unit_deg",self._lang), False, 5, 45, lw, ew)
        self.input_beta  = ParamInput(_("label_beta",self._lang), "18", _("unit_deg",self._lang), False, 0, 60, lw, ew)
        self.input_thick = ParamInput(_("label_thick",self._lang), "18", _("unit_mm",self._lang), False, 1, 200, lw, ew)
        self.input_width = ParamInput(_("label_width",self._lang), "10", _("unit_mm",self._lang), False, 1, 500, lw, ew)

        for inp in [self.input_m, self.input_z, self.input_alpha,
                     self.input_beta, self.input_thick, self.input_width]:
            inp.valueChanged.connect(self._on_params_changed)

        # 直径和预览实时更新 (每次按键都刷新)
        self.input_m.textChanged.connect(lambda _: self._on_realtime_change())
        self.input_z.textChanged.connect(lambda _: self._on_realtime_change())
        self.input_alpha.textChanged.connect(lambda _: self._on_realtime_change())
        self.input_beta.textChanged.connect(lambda _: self._on_realtime_change())
        self.input_thick.textChanged.connect(lambda _: self._on_realtime_change())
        self.input_width.textChanged.connect(lambda _: self._on_realtime_change())

        pl.addWidget(self.input_m)
        pl.addWidget(self.input_z)
        pl.addWidget(self.display_d)
        pl.addWidget(self.input_alpha)
        pl.addWidget(self.input_beta)
        pl.addWidget(self.input_thick)
        pl.addWidget(self.input_width)

        # 预览按钮 — Part 1 右下
        prev_row = QHBoxLayout()
        prev_row.addStretch()
        self.preview_btn = QPushButton(_("preview_btn",self._lang))
        self.preview_btn.setProperty("cssClass", "preview")
        self.preview_btn.setFixedSize(80, 28)
        self.preview_btn.setToolTip(_("preview_tip",self._lang))
        self.preview_btn.clicked.connect(self._toggle_preview)
        prev_row.addWidget(self.preview_btn)
        pl.addLayout(prev_row)

        ml.addWidget(self.param_group)

        # Part 2: 目标
        tg = QGroupBox(_("sec_target", self._lang))
        tl = QVBoxLayout(tg)
        tl.setSpacing(5)

        self.status_lbl = QLabel("")
        self.status_lbl.setProperty("cssClass", "status")
        self.status_lbl.setWordWrap(True)
        tl.addWidget(self.status_lbl)

        self.catia_path_panel = QWidget()
        cpl = QHBoxLayout(self.catia_path_panel)
        cpl.setContentsMargins(0, 0, 0, 0); cpl.setSpacing(4)
        self.catia_path_edit = QLineEdit()
        self.catia_path_edit.setPlaceholderText(_("catia_path_hint",self._lang))
        self.catia_path_edit.setReadOnly(True)
        cpl.addWidget(self.catia_path_edit, 1)
        self.browse_btn = QPushButton(_("browse",self._lang)); self.browse_btn.setProperty("cssClass", "secondary")
        self.browse_btn.setFixedWidth(48); self.browse_btn.clicked.connect(self._pick_catia_exe)
        cpl.addWidget(self.browse_btn)
        self.catia_path_panel.setVisible(False)
        tl.addWidget(self.catia_path_panel)

        self.file_picker = FilePicker("CATPart 文件 (*.CATPart)")
        self.file_picker.setPlaceholder(_("file_placeholder",self._lang))
        tl.addWidget(self.file_picker)

        self.import_btn = QPushButton(_("import_btn",self._lang))
        self.import_btn.setFixedHeight(34)
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self._on_import)
        tl.addWidget(self.import_btn)
        ml.addWidget(tg)
        ml.addStretch()
        QTimer.singleShot(50, self._update_diameter)

        root.addWidget(left)

        # ═══ 右面板 — 3D 预览 (默认隐藏) ═══
        self.preview_widget = GearPreviewWidget()
        self.preview_widget.setVisible(False)
        self.preview_widget.setMinimumSize(220, 220)
        root.addWidget(self.preview_widget, 1)

    # ── 预览切换 ──────────────────────────────────────

    def _toggle_preview(self):
        self._preview_open = not self._preview_open
        self.preview_widget.setVisible(self._preview_open)

        if self._preview_open:
            # 预览高度 = Part 1 高度 → 正方形
            ph = self.param_group.height()
            pw = max(ph, 220)
            self.preview_widget.setFixedWidth(pw)
            self.preview_widget.setFixedHeight(ph)
            self.setMinimumWidth(330 + pw + 20)
            self.resize(self._scaled(340) + pw + 20, self.height())
            self.preview_btn.setText(_("preview_btn_close", self._lang))
            self._update_preview()
        else:
            self.setMinimumWidth(330)
            self.resize(self._scaled(340), self.height())
            self.preview_btn.setText(_("preview_btn", self._lang))

    def _update_preview(self):
        p = self._get_params()
        if p:
            self.preview_widget.set_params(p)

    def _get_params(self):
        try:
            return GearParams(
                m=int(self.input_m.value()), z=int(self.input_z.value()),
                alpha_deg=self.input_alpha.value(), beta_deg=self.input_beta.value(),
                face_width=self.input_width.value(), tooth_thickness=self.input_thick.value())
        except ValueError:
            return None

    def _on_realtime_change(self, _=None):
        self._update_diameter()
        if self._preview_open:
            self._preview_timer.start()

    def _on_params_changed(self, _=None):
        self._update_diameter()
        if self._preview_open:
            self._preview_timer.start()

    # ── 样式 ──────────────────────────────────────────

    def _apply_style(self):
        self.setStyleSheet(get_stylesheet(self._font_size))

    # ── CATIA 检测 ───────────────────────────────────

    def _check_catia_cache(self):
        cfg = load_config()
        detected = cfg.get("catia_detected", None)
        if detected is None:
            self.status_lbl.setText(_("detecting", self._lang))
            threading.Thread(target=self._do_first_detect, daemon=True).start()
        elif detected is False:
            self._set_status.emit(_("not_found", self._lang), "#D13438")
            self.catia_path_panel.setVisible(True)
            p = cfg.get("catia_path", "");
            if p: self.catia_path_edit.setText(p)
            self.file_picker.setEnabled(True)
        else:
            self._catia_ready = True
            self._set_status.emit(_("ready", self._lang), "#107C10")
            self.file_picker.setEnabled(True)
            self.import_btn.setEnabled(True)

    def _do_first_detect(self):
        _log("首次检测 CATIA...")
        ok = CatiaConnector.detect_catia()
        save_config({"catia_detected": ok, "font_size": str(self._font_size),
                     "scale_pct": str(self._scale_pct)})
        if ok:
            self._catia_ready = True
            self._set_status.emit(_("ready", self._lang), "#107C10")
            self.file_picker.setEnabled(True)
            self.import_btn.setEnabled(True)
        else:
            self._set_status.emit(_("not_found", self._lang), "#D13438")
            self.catia_path_panel.setVisible(True)
            self.file_picker.setEnabled(True)

    def _pick_catia_exe(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 CNEXT.exe (CATIA 主程序)", "C:/",
            "CNEXT.exe (CNEXT.exe);;所有文件 (*.*)")
        if path:
            self.catia_path_edit.setText(path)
            save_config({"catia_path": path, "catia_detected": True})
            self._catia_ready = True
            self._set_status.emit(_("path_saved", self._lang), "#107C10")
            self.import_btn.setEnabled(True)

    # ── 信号槽 ───────────────────────────────────────

    def _on_show_info(self, title: str, msg: str):
        box = QMessageBox(self); box.setWindowTitle(title)
        box.setText(title); box.setIcon(QMessageBox.Information)
        box.setStandardButtons(QMessageBox.Ok); box.exec_()

    def _on_show_error(self, title: str, msg: str):
        QMessageBox.critical(self, title, msg)

    def _on_set_status(self, text: str, color: str):
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet(f"color: {color};")
        self.import_btn.setEnabled(True)

    # ── 参数 ──────────────────────────────────────────

    def _update_diameter(self, _=None):
        try:
            m = self.input_m.value(); z = self.input_z.value()
            if m > 0 and z > 0: self.display_d.set_value(m * z)
        except ValueError: pass

    # ── 导入 ──────────────────────────────────────────

    def _on_import(self):
        _log("=== Import ===")
        errors = []
        try: m = int(self.input_m.value())
        except ValueError: m = 0
        try: z = int(self.input_z.value())
        except ValueError: z = 0
        if m <= 0: errors.append(_("val_m", self._lang))
        if z <= 0: errors.append(_("val_z", self._lang))
        catpart = self.file_picker.path()
        if not catpart: errors.append(_("val_file", self._lang))
        if errors: QMessageBox.warning(self, _("input_err", self._lang), "\n".join(errors)); return
        self._set_status.emit(_("connecting", self._lang), "#616161")
        self.import_btn.setEnabled(False); self.repaint()
        threading.Thread(target=self._do_import, args=(m, z, catpart), daemon=True).start()

    def _do_import(self, m, z, catpart):
        _log(f"Import: m={m} z={z}")
        try:
            self._set_status.emit(_("connecting", self._lang), "#616161")
            manual = self.catia_path_edit.text().strip() if self.catia_path_edit.text() else ""
            ok = self._connector.connect(manual_path=manual or None)
            if not ok:
                self._show_error.emit(_("error", self._lang), _("catia_err", self._lang))
                self._set_status.emit(_("conn_fail", self._lang), "#D13438"); return
            self._set_status.emit(_("opening", self._lang), "#616161")
            doc = self._connector.is_document_open(catpart)
            if not doc: doc = self._connector.open_document(catpart)
            self._set_status.emit(_("building", self._lang), "#616161")
            params = GearParams(m=m, z=z, alpha_deg=self.input_alpha.value(),
                                beta_deg=self.input_beta.value(),
                                face_width=self.input_width.value(),
                                tooth_thickness=self.input_thick.value())
            gear_body = GearBuilder(params, doc).build(H=0.0)
            self._set_status.emit(_("success", self._lang).format(gear_body.Name), "#107C10")
            self._show_info.emit(_("done", self._lang), "")
        except Exception as e:
            tb = traceback.format_exc(); _log(f"FAIL:\n{tb}")
            self._show_error.emit(_("error", self._lang), _("build_fail", self._lang).format(str(e)[:200]))
            self._set_status.emit(_("fail", self._lang), "#D13438")

    # ── 设置 ──────────────────────────────────────────

    def _open_settings(self):
        dlg = SettingsDialog(self._font_size, self._scale_pct, self._lang, self)
        if dlg.exec_():
            fs, sc = dlg.font_size(), dlg.scale_pct()
            changed = (fs != self._font_size or sc != self._scale_pct)
            self._font_size, self._scale_pct = fs, sc
            save_config({"font_size": str(fs), "scale_pct": str(sc), "lang": self._lang})
            if changed:
                self._rebuild_ui()

    def _toggle_lang(self):
        self._lang = "en" if self._lang == "zh" else "zh"
        save_config({"lang": self._lang})
        # 直接更新所有 UI 文字 (不重建, 保持状态)
        self.setWindowTitle(_("window_title", self._lang))
        self.param_group.setTitle(_("sec_params", self._lang))
        self.input_m.lbl.setText(_("label_m", self._lang))
        self.input_z.lbl.setText(_("label_z", self._lang))
        self.display_d.lbl.setText(_("label_d", self._lang))
        self.input_alpha.lbl.setText(_("label_alpha", self._lang))
        self.input_beta.lbl.setText(_("label_beta", self._lang))
        self.input_thick.lbl.setText(_("label_thick", self._lang))
        self.input_width.lbl.setText(_("label_width", self._lang))
        self.preview_btn.setText(_("preview_btn_close", self._lang) if self._preview_open else _("preview_btn", self._lang))
        self.preview_btn.setToolTip(_("preview_tip", self._lang))
        tg = self.findChild(type(self.import_btn.parent().parent()))
        if tg: tg.setTitle(_("sec_target", self._lang))
        self.import_btn.setText(_("import_btn", self._lang))
        self.lang_btn.setText(_("lang_btn", self._lang))
        self.lang_btn.setToolTip(_("lang_tip", self._lang))
        self.settings_btn.setToolTip(_("settings", self._lang))
        self.browse_btn.setText(_("browse", self._lang))
        self.catia_path_edit.setPlaceholderText(_("catia_path_hint", self._lang))
        self.file_picker.setPlaceholder(_("file_placeholder", self._lang))
        # 更新状态文字
        if self._catia_ready:
            self._set_status.emit(_("ready", self._lang), "#107C10")

    def _rebuild_ui(self):
        w, h = self._scaled(340, 470)
        if self._preview_open:
            pw = self.preview_widget.width()
            w += pw + 20
        self.resize(w, h)
        self._apply_style()
        lw, ew = self._scaled(60), self._scaled(100)
        for inp in [self.input_m, self.input_z, self.input_alpha,
                     self.input_beta, self.input_thick, self.input_width]:
            inp.lbl.setFixedWidth(lw); inp.input.setFixedWidth(ew)
        self.display_d.lbl.setFixedWidth(lw)
        self.display_d.val_lbl.setFixedWidth(ew)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._preview_open:
            # 预览正方形，高度跟随 Part 1
            ph = max(self.param_group.height(), 220)
            self.preview_widget.setFixedHeight(ph)
            self.preview_widget.setFixedWidth(ph)
            # 更新 OpenGL 视口
            self.preview_widget.update()
