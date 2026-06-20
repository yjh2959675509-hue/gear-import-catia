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

1. Double-click `齿轮一键导入.exe`
2. Input parameters → press Enter to confirm
3. Select target .CATPart file
4. Click **Import**

## Requirements (Dev)

- Python 3.10+
- PyQt5, PyOpenGL, pywin32
- CATIA V5 (any version)

## Build

```bash
conda activate gear_catia
python build.py
```

## Author

Kerman Yuan & DeepSeek-V4

## License

MIT — see [LICENSE](LICENSE)
