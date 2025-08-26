#!/usr/bin/env python3
"""
Vercel用エントリーポイント
"""

from app import app

# Vercel用のハンドラー関数
def handler(event, context):
    return app

# エクスポート
application = app
