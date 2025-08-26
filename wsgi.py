#!/usr/bin/env python3
"""
Vercel用WSGIエントリーポイント
"""

from app import app

# Vercel用のハンドラー関数
def handler(request, response):
    return app(request, response)

# 通常のWSGI用
application = app

if __name__ == "__main__":
    app.run()
