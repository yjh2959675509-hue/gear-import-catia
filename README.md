# Gear Import CATIA

Parametric involute spur/helical gear import for CATIA V5 with real-time 3D preview.

## Features

- One-click gear import into CATIA Part (.CATPart)
- Real-time 3D OpenGL preview with mouse rotation & zoom
- Spur & helical gear support
- Auto-detect CATIA installation (multi-version V5R20-R27)
- CN/EN bilingual UI
- MIT License

## Quick Start

1. Double-click `GearImportCATIA-v2.2.exe`
2. Input parameters → press Enter to confirm
3. Select target .CATPart file
4. Click **Import**

## Development

### Environment

| Tool | Version | Notes |
|------|---------|-------|
| Windows | 10 / 11 | Required for CATIA COM |
| Miniconda | latest | Python environment manager |
| Python | 3.10 | Managed by conda |
| CATIA | V5 R20-R27 | V5R21 tested |

### Setup

```bash
# 1. Install Miniconda from https://docs.conda.io/en/latest/miniconda.html

# 2. Create dedicated environment
conda create -n gear_catia python=3.10 -y
conda activate gear_catia

# 3. Install dependencies
pip install pywin32 PyQt5 PyOpenGL PyOpenGL_accelerate PyInstaller
```

### Build

```bash
conda activate gear_catia
python build.py
```

Output: `齿轮一键导入.exe` (single-file, ~50 MB)

### Project Structure

```
src/
├── main.py              # Entry point
├── gear/
│   ├── params.py        # Gear parameter calculation
│   └── involute.py      # Involute curve generation
├── catia/
│   ├── connector.py     # CATIA COM connection (multi-version)
│   ├── gear_builder.py  # Gear geometry construction
│   └── naming.py        # Per-CATPart auto-increment naming
├── ui/
│   ├── main_window.py   # Main window
│   ├── gear_preview.py  # 3D OpenGL preview
│   ├── settings_dialog.py
│   ├── widgets.py       # Custom input widgets
│   ├── styles.py        # Win11 QSS stylesheet
│   └── i18n.py          # CN/EN translations
└── resources/
    └── icon.ico
```

## Author

Kerman Yuan & DeepSeek-V4

## License

MIT — see [LICENSE](LICENSE)
