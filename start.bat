@echo off
title 仓库系统启动器
color 0A

echo ========================================
echo         仓库系统一键启动
echo ========================================
echo.

:: 启动 MySQL
echo [1/4] 启动 MySQL...
net start MySQL80 >nul 2>&1
if %errorlevel% == 0 (
    echo       MySQL 启动成功
) else (
    echo       MySQL 已在运行
)

:: 启动后端
echo [2/4] 启动后端...
start "后端 API" cmd /k "cd /d D:\projects\warehouse-system\backend && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

:: 启动管理端
echo [3/4] 启动管理端...
start "管理端 Admin" cmd /k "cd /d D:\projects\warehouse-system\frontend-admin && npm run dev -- --host --port 5173"
timeout /t 2 /nobreak >nul

:: 启动客户端
echo [4/4] 启动客户端...
start "客户端 Client" cmd /k "cd /d D:\projects\warehouse-system\frontend-client && npm run dev -- --host --port 5174"

echo.
echo ========================================
echo   全部启动完成！
echo   后端：    http://192.168.0.109:8000
echo   管理端：  http://192.168.0.109:5173
echo   客户端：  http://192.168.0.109:5174
echo ========================================
echo.
pause