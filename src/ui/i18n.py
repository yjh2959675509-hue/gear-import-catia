"""i18n 国际化 — 中/英双语支持."""

T = {
    # ── 窗口标题 ──
    "window_title": {"zh": "齿轮一键导入 CATIA", "en": "Gear Import CATIA"},
    "header":      {"zh": "齿轮参数化导入",     "en": "Parametric Gear Import"},

    # ── 参数区 ──
    "sec_params":  {"zh": "参数选择",       "en": "Parameters"},
    "label_m":     {"zh": "模数 m",         "en": "Module m"},
    "label_z":     {"zh": "齿数 z",         "en": "Teeth z"},
    "label_d":     {"zh": "分度圆 d",       "en": "Pitch Dia. d"},
    "label_alpha": {"zh": "压力角 α",       "en": "Pressure α"},
    "label_beta":  {"zh": "螺旋角 β",       "en": "Helix β"},
    "label_thick": {"zh": "齿厚",           "en": "Tooth Thick"},
    "label_width": {"zh": "齿宽",           "en": "Face Width"},
    "unit_mm":     {"zh": "mm",             "en": "mm"},
    "unit_deg":    {"zh": "°",              "en": "°"},

    # ── 预览 ──
    "preview_btn":  {"zh": "▶ 预览",             "en": "▶ Preview"},
    "preview_btn_close": {"zh": "◀ 预览",        "en": "◀ Preview"},
    "preview_tip":  {"zh": "可视化预览齿轮",     "en": "Visual gear preview"},

    # ── 目标区 ──
    "sec_target":    {"zh": "目标 CATIA Part", "en": "Target CATIA Part"},
    "catia_path_hint": {"zh": "手动选择 CNEXT.exe ...", "en": "Locate CNEXT.exe ..."},
    "browse":        {"zh": "浏览",            "en": "Browse"},
    "file_placeholder": {"zh": "选择目标 .CATPart 文件...", "en": "Select .CATPart file..."},
    "import_btn":    {"zh": "导  入",          "en": "Import"},

    # ── CATIA 状态 ──
    "detecting":   {"zh": "首次运行, 正在检测 CATIA ...", "en": "First run, detecting CATIA..."},
    "ready":       {"zh": "CATIA 已就绪 — 选择文件后点导入", "en": "CATIA ready — select file and import"},
    "not_found":   {"zh": "CATIA 未安装, 请手动定位 CNEXT.exe", "en": "CATIA not found. Locate CNEXT.exe manually."},
    "path_saved":  {"zh": "CATIA 路径已保存", "en": "CATIA path saved"},
    "connecting":  {"zh": "正在连接 CATIA ...", "en": "Connecting to CATIA..."},
    "opening":     {"zh": "正在打开文件 ...",   "en": "Opening file..."},
    "building":    {"zh": "正在生成齿轮 ...",   "en": "Building gear..."},
    "success":     {"zh": "成功: {}",            "en": "OK: {}"},
    "fail":        {"zh": "导入失败",            "en": "Import failed"},
    "conn_fail":   {"zh": "连接失败",            "en": "Connection failed"},

    # ── 弹窗 ──
    "input_err":   {"zh": "输入错误",  "en": "Input Error"},
    "error":       {"zh": "错误",      "en": "Error"},
    "done":        {"zh": "导入成功",  "en": "Import OK"},
    "catia_err":   {"zh": "无法连接 CATIA\n\n如自动检测失败, 请手动指定 CNEXT.exe",
                    "en": "Cannot connect to CATIA.\n\nIf auto-detect fails, locate CNEXT.exe manually."},
    "build_fail":  {"zh": "齿轮生成出错: {}", "en": "Gear build error: {}"},

    # ── 验证 ──
    "val_m":       {"zh": "- 模数 m 无效",    "en": "- Module m invalid"},
    "val_z":       {"zh": "- 齿数 z 无效",    "en": "- Teeth z invalid"},
    "val_file":    {"zh": "- 请选择目标 CATPart 文件", "en": "- Select target CATPart file"},

    # ── 设置 ──
    "settings":    {"zh": "设置",       "en": "Settings"},
    "font_size":   {"zh": "字体大小",   "en": "Font Size"},
    "ui_scale":    {"zh": "界面缩放",   "en": "UI Scale"},
    "btn_source":  {"zh": "源代码",     "en": "Source Code"},
    "btn_devlog":  {"zh": "开发日志",   "en": "Dev Log"},
    "lang_btn":    {"zh": "EN",         "en": "中"},
    "lang_tip":    {"zh": "切换语言",   "en": "Switch Language"},

    # ── 源代码窗口 ──
    "source_title": {"zh": "源代码 — MIT 开源协议", "en": "Source Code — MIT License"},
    "mit_header": {"zh": (
        "# MIT License\n"
        "# Copyright (c) 2026 Kerman Yuan & DeepSeek-V4\n"
        "#\n"
        "# Permission is hereby granted, free of charge, to any person obtaining a copy\n"
        "# of this software and associated documentation files (the \"Software\"), to deal\n"
        "# in the Software without restriction, including without limitation the rights\n"
        "# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
        "# copies of the Software, and to permit persons to whom the Software is\n"
        "# furnished to do so, subject to the following conditions:\n"
        "#\n"
        "# The above copyright notice and this permission notice shall be included in all\n"
        "# copies or substantial portions of the Software.\n"
        "#\n"
        "# https://github.com/yjh2959675509-hue/gear-import-catia\n"
        "#\n"
        "# THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
        "# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
        "# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
        "# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
        "# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
        "# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
        "# SOFTWARE.\n\n"
    ), "en": (
        "# MIT License\n"
        "# Copyright (c) 2026 Kerman Yuan & DeepSeek-V4\n"
        "#\n"
        "# Permission is hereby granted, free of charge, to any person obtaining a copy\n"
        "# of this software and associated documentation files (the \"Software\"), to deal\n"
        "# in the Software without restriction, including without limitation the rights\n"
        "# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
        "# copies of the Software, and to permit persons to whom the Software is\n"
        "# furnished to do so, subject to the following conditions:\n"
        "#\n"
        "# The above copyright notice and this permission notice shall be included in all\n"
        "# copies or substantial portions of the Software.\n"
        "#\n"
        "# https://github.com/yjh2959675509-hue/gear-import-catia\n"
        "#\n"
        "# THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
        "# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
        "# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
        "# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
        "# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
        "# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
        "# SOFTWARE.\n\n"
    )},

    # ── 开发日志 ──
    "devlog_title": {"zh": "开发日志", "en": "Development Log"},
    "devlog_content": {"zh": (
        "══════════════════════════════════════\n"
        "  齿轮一键导入 CATIA — 开发日志\n"
        "  Kerman Yuan & DeepSeek-V4\n"
        "══════════════════════════════════════\n\n"
        "【V1.0】 基础架构\n"
        "  · CATIA COM 连接器 (多版本 V5R20-R27 注册表检测)\n"
        "  · 齿轮参数计算 (模数/齿数/压力角/螺旋角)\n"
        "  · Win11 Fluent Design QSS 样式表\n\n"
        "【V1.1】 CATIA 齿轮构建\n"
        "  · HybridShapeFactory 渐开线样条 + 齿形轮廓\n"
        "  · Pad → Slot/Pocket → CircularPattern\n"
        "  · 直齿轮 + 斜齿轮双路径\n\n"
        "【V1.2】 GUI 完善\n"
        "  · 参数实时验证 + 分度圆 d 动态更新\n"
        "  · CATPart 文件浏览器 + 自动/手动 CATIA 定位\n"
        "  · 界面缩放 + 字体大小设置\n\n"
        "【V1.3】 命名与健壮性\n"
        "  · 每个 CATPart 独立命名 (齿轮(1)(2)...)\n"
        "  · 已打开文件直接写入, 未打开自动先打开\n\n"
        "【V2.0】 3D 实时预览\n"
        "  · OpenGL + QOpenGLWidget 渲染\n"
        "  · 统一 Mesh 架构 (侧面+端盖共享顶点)\n"
        "  · 端盖纯平法线 → 无闪烁\n"
        "  · 三光源布光 (Key+Fill+Rim)\n"
        "  · 左键旋转 + 滚轮缩放\n\n"
        "【V2.1】 渲染优化\n"
        "  · 16 层 body 切片 → 侧面平滑\n"
        "  · MSAA 4x 多重采样\n"
        "  · 高光材质 + 暗背景对比\n"
        "  · 裁剪面自适应大小齿轮\n\n"
        "【V2.2】 国际化\n"
        "  · 中/英双语切换\n"
        "  · MIT 开源协议\n"
        "  · 源代码 + 开发日志查看\n"
    ), "en": (
        "══════════════════════════════════════\n"
        "  Gear Import CATIA — Dev Log\n"
        "  Kerman Yuan & DeepSeek-V4\n"
        "══════════════════════════════════════\n\n"
        "[V1.0] Foundation\n"
        "  · CATIA COM connector (multi-version V5R20-R27)\n"
        "  · Gear parameter calculation\n"
        "  · Win11 Fluent Design QSS stylesheet\n\n"
        "[V1.1] CATIA Gear Builder\n"
        "  · HybridShapeFactory involute spline\n"
        "  · Pad → Slot/Pocket → CircularPattern\n"
        "  · Spur + Helical dual path\n\n"
        "[V1.2] GUI Refinement\n"
        "  · Real-time param validation + d update\n"
        "  · File browser + auto/manual CATIA locate\n"
        "  · UI scale + font size settings\n\n"
        "[V1.3] Naming & Robustness\n"
        "  · Per-CATPart naming (Gear(1)(2)...)\n"
        "  · Open file directly or auto-open\n\n"
        "[V2.0] 3D Real-time Preview\n"
        "  · OpenGL + QOpenGLWidget rendering\n"
        "  · Unified mesh architecture\n"
        "  · Flat cap normals → zero flicker\n"
        "  · 3-point lighting (Key+Fill+Rim)\n"
        "  · Left-drag rotate + wheel zoom\n\n"
        "[V2.1] Render Optimization\n"
        "  · 16 body slices → smooth sides\n"
        "  · MSAA 4x multi-sampling\n"
        "  · Specular material + dark background\n"
        "  · Adaptive clip planes for all gear sizes\n\n"
        "[V2.2] Internationalization\n"
        "  · CN/EN bilingual toggle\n"
        "  · MIT open source license\n"
        "  · Source code + dev log viewer\n"
    )},
}


def _(key, lang="zh", **kwargs):
    """获取翻译文本。"""
    s = T.get(key, {}).get(lang, key)
    if kwargs:
        s = s.format(**kwargs)
    return s
