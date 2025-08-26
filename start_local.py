#!/usr/bin/env python3
"""
空気清浄機販売営業管理システム - ローカル起動スクリプト

このスクリプトはローカル環境での起動を簡単にし、
一般的な問題を自動で解決します。

使用方法:
    python start_local.py
"""

import os
import sys
import subprocess
import platform
import socket
import time
import webbrowser
from pathlib import Path

def check_python_version():
    """Pythonバージョンチェック"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8以上が必要です")
        print(f"現在のバージョン: {sys.version}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """依存関係チェック"""
    required_packages = ['flask', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} インストール済み")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} が見つかりません")
    
    if missing_packages:
        print(f"\n📦 不足パッケージをインストールします...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, 
                         check=True, capture_output=True)
            print("✅ パッケージのインストールが完了しました")
        except subprocess.CalledProcessError as e:
            print(f"❌ パッケージのインストールに失敗しました: {e}")
            return False
    
    return True

def find_free_port(start_port=5000, max_attempts=20):
    """利用可能なポートを検出"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def kill_port_process(port):
    """指定ポートを使用しているプロセスを終了"""
    system = platform.system().lower()
    
    try:
        if system == "darwin" or system == "linux":  # macOS or Linux
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    print(f"🔄 ポート {port} を使用中のプロセス {pid} を終了します...")
                    subprocess.run(['kill', '-9', pid], capture_output=True)
                return True
        elif system == "windows":
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port} ' in line and 'LISTENING' in line:
                    parts = line.split()
                    if parts:
                        pid = parts[-1]
                        print(f"🔄 ポート {port} を使用中のプロセス {pid} を終了します...")
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        return True
    except Exception as e:
        print(f"⚠️  プロセス終了中にエラー: {e}")
    
    return False

def suggest_airplay_fix():
    """AirPlay Receiverの無効化方法を案内"""
    if platform.system().lower() == "darwin":  # macOS
        print("\n💡 macOSでポート5000が使用中の場合:")
        print("   1. システム設定 → 一般 → AirDrop とHandoff")
        print("   2. 'AirPlay Receiver' をオフに設定")
        print("   3. アプリケーションを再起動")
        print()

def create_desktop_shortcut():
    """デスクトップショートカット作成（オプション）"""
    try:
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            shortcut_content = f"""#!/bin/bash
cd "{os.getcwd()}"
python start_local.py
"""
            shortcut_path = desktop / "営業管理システム.command"
            with open(shortcut_path, 'w', encoding='utf-8') as f:
                f.write(shortcut_content)
            
            os.chmod(shortcut_path, 0o755)
            print(f"🖥️  デスクトップショートカットを作成しました: {shortcut_path}")
    except Exception as e:
        print(f"⚠️  ショートカット作成エラー: {e}")

def main():
    """メイン処理"""
    print("\n" + "="*70)
    print("🚀 空気清浄機販売営業管理システム - ローカル起動ツール")
    print("="*70)
    
    # システムチェック
    print("📋 システム環境チェック...")
    
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # ポートチェック
    print("\n🔍 利用可能なポートを検索中...")
    port = find_free_port(5000, 20)
    
    if not port:
        print("❌ 利用可能なポートが見つかりません")
        suggest_airplay_fix()
        
        # ポート5000を強制的に解放を試行
        print("🔄 ポート5000の解放を試行します...")
        if kill_port_process(5000):
            port = 5000
        else:
            print("❌ ポートの解放に失敗しました")
            sys.exit(1)
    
    print(f"✅ ポート {port} を使用します")
    
    # 環境変数設定
    os.environ['PORT'] = str(port)
    os.environ['FLASK_DEBUG'] = 'true'
    
    print("\n🎯 アプリケーション起動準備完了!")
    print(f"📍 アクセスURL: http://127.0.0.1:{port}")
    
    # デスクトップショートカット作成（初回のみ）
    shortcut_path = Path.home() / "Desktop" / "営業管理システム.command"
    if not shortcut_path.exists():
        create_desktop_shortcut()
    
    print("\n⚡ サーバーを起動しています...")
    print("   (停止するには Ctrl+C を押してください)")
    print("="*70)
    
    # ブラウザ自動起動
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open(f'http://127.0.0.1:{port}')
        except:
            pass
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # メインアプリケーション起動
    try:
        from app import app
        app.run(debug=True, host='127.0.0.1', port=port, threaded=True)
    except KeyboardInterrupt:
        print("\n\n⛔ サーバーを停止しました")
        print("👋 ご利用ありがとうございました！")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print("\n💡 トラブルシューティング:")
        print("   1. アプリディレクトリで実行しているか確認")
        print("   2. 必要なファイルが存在するか確認")
        print("   3. Python環境を確認")
        sys.exit(1)

if __name__ == "__main__":
    main()
