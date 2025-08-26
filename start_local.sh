#!/bin/bash

# 空気清浄機販売営業管理システム - ローカル起動スクリプト (macOS/Linux)

echo ""
echo "======================================================================"
echo "🚀 空気清浄機販売営業管理システム - ローカル起動ツール"
echo "======================================================================"

# Pythonバージョンチェック
echo "📋 Python環境チェック中..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3がインストールされていません"
    echo "💡 https://python.org からPython 3.8以上をインストールしてください"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION 確認完了"

# 依存関係チェック
echo ""
echo "📦 依存関係チェック中..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Flaskをインストールしています..."
    python3 -m pip install flask requests
fi

echo "✅ 依存関係確認完了"

# macOSの場合、AirPlay Receiverの警告
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "💡 macOSユーザーへの注意:"
    echo "   ポート5000エラーが発生する場合は、"
    echo "   システム設定 → 一般 → AirDrop とHandoff → AirPlay Receiver をオフ"
fi

echo ""
echo "⚡ アプリケーションを起動しています..."
echo "📍 ブラウザが自動で開きます"
echo "🛑 停止するには Ctrl+C を押してください"
echo "======================================================================"
echo ""

# アプリケーション起動
python3 start_local.py

echo ""
echo "👋 ご利用ありがとうございました！"
