@echo off
chcp 65001 > nul
title 空気清浄機販売営業管理システム

echo.
echo ====================================================================
echo 🚀 空気清浄機販売営業管理システム - ローカル起動ツール (Windows)
echo ====================================================================

echo 📋 Python環境チェック中...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Pythonがインストールされていません
    echo 💡 https://python.org からPython 3.8以上をインストールしてください
    pause
    exit /b 1
)

echo ✅ Python環境確認完了
echo.

echo 📦 依存関係チェック中...
pip show flask > nul 2>&1
if errorlevel 1 (
    echo 📦 Flaskをインストールしています...
    pip install flask requests
)

echo ✅ 依存関係確認完了
echo.

echo ⚡ アプリケーションを起動しています...
echo 📍 ブラウザが自動で開きます
echo 🛑 停止するには Ctrl+C を押してください
echo ====================================================================
echo.

python start_local.py

echo.
echo 👋 ご利用ありがとうございました！
pause
