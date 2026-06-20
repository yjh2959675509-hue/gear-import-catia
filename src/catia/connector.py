"""CATIA COM 连接器。

模式 (参考 CATIA-IN 项目):
  首次运行: Dispatch + Quit 检测是否安装 → 缓存结果
  后续: 读缓存，不重复检测
  导入时: GetActiveObject → Dispatch(轮询) → subprocess.Popen

改进点 vs CATIA-IN:
  - 多 ProgID 备选提升检测成功率
  - 轮询替代固定 sleep 提升效率
"""

import os
import json
import time
import subprocess
import win32com.client
import pythoncom

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".gear_catia_config")

# CATIA ProgID 备选列表 (按优先级)
_PROGIDS = [
    "CATIA.Application",       # 标准注册 (V5R20+)
    "CATIA.V5.Application",    # 部分旧版安装
]


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg: dict):
    existing = load_config()
    existing.update(cfg)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False)
    except Exception:
        pass


def _try_get_active_object():
    """尝试连接已运行的 CATIA (遍历所有已知 ProgID)."""
    for pid in _PROGIDS:
        try:
            return win32com.client.GetActiveObject(pid)
        except Exception:
            continue
    return None


def _try_dispatch():
    """尝试启动 CATIA (遍历所有已知 ProgID)."""
    for pid in _PROGIDS:
        try:
            return win32com.client.Dispatch(pid)
        except Exception:
            continue
    return None


class CatiaConnector:
    """CATIA COM 连接器."""

    def __init__(self):
        self.app = None
        self._started_by_us = False
        self._progid = None

    # ── 检测 (首次) ───────────────────────────────────

    @staticmethod
    def detect_catia():
        """检测 CATIA — Dispatch + Quit，多 ProgID 备选。"""
        for pid in _PROGIDS:
            try:
                app = win32com.client.Dispatch(pid)
                app.Quit()
                # 缓存成功的 ProgID
                save_config({"catia_progid": pid})
                return True
            except Exception:
                continue
        return False

    @property
    def is_detected(self):
        return load_config().get("catia_detected", None)

    # ── 连接 (导入时调用) ──────────────────────────────

    def connect(self, manual_path: str = None):
        """连接 CATIA。优先已运行实例，否则启动。"""
        pythoncom.CoInitialize()

        # ── 1) 连接已运行的 CATIA ──
        app = _try_get_active_object()
        if app is not None:
            self.app = app
            self._started_by_us = False
            return True

        # ── 2) COM Dispatch 自动启动 + 轮询等待就绪 ──
        app = _try_dispatch()
        if app is not None:
            self.app = app
            self.app.Visible = True
            self._started_by_us = True
            # 轮询等待 COM 完全就绪 (替代固定 sleep)
            self._wait_ready(timeout=8.0)
            return True

        # ── 3) 手动路径: subprocess + 轮询 ──
        catia_exe = manual_path or load_config().get("catia_path", "")
        if catia_exe and os.path.isfile(catia_exe):
            subprocess.Popen([catia_exe], shell=False)
            # CATIA 启动后反复尝试 GetActiveObject
            for _ in range(40):
                time.sleep(0.75)
                app = _try_get_active_object()
                if app is not None:
                    self.app = app
                    self.app.Visible = True
                    self._started_by_us = True
                    # 保存路径以便下次使用
                    save_config({"catia_path": catia_exe})
                    return True

        return False

    def _wait_ready(self, timeout: float = 8.0):
        """轮询等待 CATIA COM 就绪。每 200ms 检查一次。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(0.2)
            app = _try_get_active_object()
            if app is not None:
                # 确认 Visible 已设置
                try:
                    app.Visible = True
                except Exception:
                    pass
                return True
        return False

    def is_connected(self) -> bool:
        return self.app is not None

    # ── 文档操作 ──────────────────────────────────────

    def open_document(self, path: str):
        path = os.path.normpath(path)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")
        return self.app.Documents.Open(path)

    def is_document_open(self, path: str):
        path = os.path.normcase(os.path.normpath(path))
        for i in range(1, self.app.Documents.Count + 1):
            doc = self.app.Documents.Item(i)
            try:
                dp = os.path.normcase(os.path.normpath(doc.FullName))
                if dp == path:
                    return doc
            except Exception:
                pass
        return None


_connector = None


def get_connector() -> CatiaConnector:
    global _connector
    if _connector is None:
        _connector = CatiaConnector()
    return _connector
