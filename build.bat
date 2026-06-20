@echo off
chcp 65001 > nul
echo === 齿轮一键导入 - 构建 ===
echo.
call D:\File\application\Miniconda\Scripts\activate.bat gear_catia
python build.py
if %ERRORLEVEL% NEQ 0 (
    echo 构建失败，检查上方错误信息。
    pause
) else (
    echo 构建完成！
)
