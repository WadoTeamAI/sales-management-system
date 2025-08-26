# 🚀 空気清浄機販売営業管理システム - デプロイメントガイド

## 📋 概要

このWebアプリケーションを各種プラットフォームにデプロイする手順を説明します。

## 🌐 サポートされるプラットフォーム

### 1. Vercel（最新推奨）

#### 必要なファイル
- `vercel.json`: Vercel設定ファイル
- `wsgi.py`: WSGIエントリーポイント
- `requirements.txt`: Python依存関係

#### デプロイ手順

```bash
# 1. Vercel CLIインストール（未インストールの場合）
npm install -g vercel

# 2. Vercelログイン
vercel login

# 3. プロジェクトディレクトリで初期化
vercel

# 4. 本番デプロイ
vercel --prod
```

#### 環境変数設定

```bash
# Vercel Dashboard または CLI で設定
vercel env add SECRET_KEY production
# 安全なランダム文字列を入力

vercel env add FLASK_ENV production
# "production" を入力

vercel env add FLASK_DEBUG production  
# "false" を入力
```

### 2. Render.com（Flask推奨）

#### 必要なファイル
- `render.yaml`: Render設定ファイル

#### デプロイ手順

1. Render.comにGitHubアカウントでログイン
2. 「New」→「Web Service」
3. GitHubリポジトリを選択
4. 設定は `render.yaml` から自動読み込み
5. 「Create Web Service」をクリック

### 3. Heroku（従来推奨）

#### 必要なファイル
- `Procfile`: Heroku用の起動設定
- `requirements.txt`: Python依存関係
- `app.py`: メインアプリケーション

#### デプロイ手順

```bash
# 1. Heroku CLIインストール（未インストールの場合）
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Herokuログイン
heroku login

# 3. Herokuアプリケーション作成
heroku create sales-management-app-[your-name]

# 4. Herokuにデプロイ
git push heroku main

# 5. アプリケーションを開く
heroku open
```

#### 環境変数設定

```bash
# 本番環境設定
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key-here

# デバッグ無効化
heroku config:set FLASK_DEBUG=false
```

### 2. Render.com

#### デプロイ手順

1. GitHub リポジトリをRender.comに接続
2. 新しいWebサービスを作成
3. 設定:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3

### 3. Railway.app

#### デプロイ手順

1. Railway.appにGitHubアカウントでログイン
2. 「New Project」→「Deploy from GitHub repo」
3. リポジトリを選択
4. 自動デプロイが開始

### 4. DigitalOcean App Platform

#### デプロイ手順

1. DigitalOcean App Platformにアクセス
2. 「Create App」→「GitHub」
3. リポジトリを選択
4. アプリ設定:
   - **Source Directory**: `/`
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `python app.py`

## 🔧 ローカル開発環境

### 環境構築

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境有効化
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 依存関係インストール
pip install -r requirements.txt

# アプリケーション起動
python app.py
```

### アクセス

- **URL**: http://127.0.0.1:5000
- **デモユーザー**: 
  - `u001` - 田中太郎（営業担当）
  - `u002` - 佐藤花子（営業担当）
  - `u003` - 山田次郎（チームリーダー）
  - `u004` - 鈴木一郎（マネージャー）

## 📊 システム要件

### 最小システム要件

- **Python**: 3.8以上
- **メモリ**: 512MB以上
- **ストレージ**: 100MB以上

### 推奨システム要件

- **Python**: 3.9以上
- **メモリ**: 1GB以上
- **ストレージ**: 500MB以上

## 🔒 セキュリティ設定

### 本番環境での重要な設定

```python
# app.py内で設定変更
app.secret_key = os.environ.get('SECRET_KEY', 'your-production-secret-key')

# デバッグモード無効化
debug_mode = False
```

### 環境変数

```bash
# 必須環境変数
SECRET_KEY=your-very-secure-secret-key
FLASK_ENV=production
FLASK_DEBUG=false

# オプション環境変数
PORT=5000
HOST=0.0.0.0
```

## 📈 パフォーマンス最適化

### 本番環境推奨設定

1. **Gunicorn使用**:
   ```bash
   gunicorn --bind 0.0.0.0:$PORT app:app
   ```

2. **ワーカー数調整**:
   ```bash
   gunicorn --workers 4 --bind 0.0.0.0:$PORT app:app
   ```

3. **静的ファイル配信最適化**:
   - CDNの利用を検討
   - Nginxリバースプロキシ設定

## 🔍 トラブルシューティング

### よくある問題

1. **ポートエラー**
   ```
   解決策: 環境変数PORTを正しく設定
   ```

2. **テンプレート読み込みエラー**
   ```
   解決策: templates/ディレクトリが存在することを確認
   ```

3. **静的ファイル404エラー**
   ```
   解決策: static/ディレクトリの権限を確認
   ```

## 📞 サポート

デプロイに関する質問や問題が発生した場合:

- **GitHub Issues**: プロジェクトリポジトリのIssues
- **Email**: support@yourcompany.com

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**Happy Deployment! 🎉**
