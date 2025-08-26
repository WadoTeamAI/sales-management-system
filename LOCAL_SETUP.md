# 🏠 ローカル環境セットアップガイド

## 🎯 概要

このガイドでは、空気清浄機販売営業管理システムをローカル環境で簡単に起動する方法を説明します。

## 🚀 クイックスタート

### 1. **最も簡単な方法**

#### Windows の場合
```cmd
start_local.bat をダブルクリック
```

#### macOS/Linux の場合
```bash
./start_local.sh
```

または

```bash
python3 start_local.py
```

### 2. **手動起動**

```bash
# 標準起動（ポート自動検出）
python app.py

# 特定ポートで起動
PORT=8080 python app.py
```

## 🔧 システム要件

### 必須要件
- **Python**: 3.8以上
- **OS**: Windows 10/macOS 10.15/Ubuntu 18.04 以上
- **メモリ**: 512MB以上
- **ディスク容量**: 100MB以上

### 推奨要件
- **Python**: 3.9以上
- **メモリ**: 1GB以上
- **ブラウザ**: Chrome, Firefox, Safari 最新版

## 📦 インストール手順

### Step 1: リポジトリクローン

```bash
git clone https://github.com/[your-username]/sales-management-system.git
cd sales-management-system
```

### Step 2: 依存関係インストール

```bash
pip install -r requirements.txt
```

### Step 3: アプリケーション起動

```bash
python start_local.py
```

## 🌐 アクセス方法

起動後、自動でブラウザが開きます。手動でアクセスする場合：

- **URL**: http://127.0.0.1:[port番号]
- **ポート**: 自動検出（通常5000-5020の範囲）

## 👥 デモユーザー

| ユーザーID | 名前 | 役職 | 権限 |
|-----------|------|------|------|
| u001 | 田中太郎 | 営業担当 | 個人データ管理 |
| u002 | 佐藤花子 | 営業担当 | 個人データ管理 |
| u003 | 山田次郎 | チームリーダー | チーム管理 |
| u004 | 鈴木一郎 | マネージャー | 全体管理 |

## 🔍 トラブルシューティング

### よくある問題と解決策

#### 1. **「ポートが使用中」エラー**

**問題**: `Address already in use` エラー

**解決策**:
- **macOS**: システム設定 → 一般 → AirDrop とHandoff → AirPlay Receiver をオフ
- **Windows**: タスクマネージャーで該当プロセスを終了
- **共通**: 別のポートを指定 `PORT=8080 python app.py`

#### 2. **「モジュールが見つからない」エラー**

**問題**: `ModuleNotFoundError: No module named 'flask'`

**解決策**:
```bash
pip install -r requirements.txt
```

または個別インストール:
```bash
pip install flask requests
```

#### 3. **「権限エラー」（macOS/Linux）**

**問題**: `Permission denied`

**解決策**:
```bash
chmod +x start_local.sh start_local.py
```

#### 4. **ブラウザが自動で開かない**

**解決策**:
手動で以下にアクセス:
- http://127.0.0.1:5000
- http://localhost:5000

#### 5. **画面が崩れて表示される**

**解決策**:
1. ブラウザのキャッシュクリア
2. ブラウザの更新（F5）
3. 別のブラウザで試行

## ⚡ パフォーマンス最適化

### 開発時の設定

```bash
# デバッグモード有効
export FLASK_DEBUG=true

# 自動リロード有効
export FLASK_ENV=development
```

### 本番近似環境

```bash
# デバッグモード無効
export FLASK_DEBUG=false
export FLASK_ENV=production

# Gunicornで起動（推奨）
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

## 🎨 カスタマイズ

### ポート番号固定

`app.py` の `find_free_port(5000)` を `find_free_port(8080)` に変更

### デバッグモード無効

`app.py` の `debug_mode = True` を `debug_mode = False` に変更

### ログレベル変更

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR
```

## 🔒 セキュリティ注意事項

### ローカル開発時

- **ホスト制限**: `127.0.0.1` に限定（デフォルト）
- **デバッグモード**: 本番では無効化必須
- **秘密キー**: 本番では環境変数で設定

### ネットワーク公開する場合

```bash
# 注意: セキュリティリスクがあります
HOST=0.0.0.0 python app.py
```

## 📱 動作確認済み環境

### OS
- ✅ Windows 11 Pro
- ✅ macOS Ventura 13.0
- ✅ Ubuntu 22.04 LTS
- ✅ CentOS 8

### Python
- ✅ Python 3.8.x
- ✅ Python 3.9.x  
- ✅ Python 3.10.x
- ✅ Python 3.11.x

### ブラウザ
- ✅ Chrome 100+
- ✅ Firefox 100+
- ✅ Safari 15+
- ✅ Edge 100+

## 🆘 サポート

### 問題が解決しない場合

1. **ログ確認**: ターミナル/コマンドプロンプトのエラーメッセージ
2. **環境確認**: `python --version`, `pip --version`
3. **再インストール**: 依存関係の再インストール
4. **イシュー報告**: GitHub Issues で報告

### 連絡先

- **GitHub Issues**: [プロジェクトページ](https://github.com/[username]/sales-management-system/issues)
- **Email**: support@yourcompany.com

---

## 🎉 お疲れさまでした！

システムが正常に起動できましたら、営業管理システムの全機能をお楽しみください！

- 📊 ダッシュボードで統計確認
- 📝 日報作成・管理
- 🎯 目標設定・進捗管理
- 📦 商品カタログ閲覧
- 📈 売上分析
- 👥 チーム管理

**Happy Coding! 🚀**
