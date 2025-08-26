#!/usr/bin/env python3
"""
空気清浄機販売営業向け日報・目標管理システム - Webアプリケーション
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, date, timedelta
import logging
import json
from typing import Dict, Any

# 既存のサービスをインポート
from main_app import SalesManagementApp
from models import UserRole, TargetType

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flaskアプリケーション初期化
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# グローバルアプリケーションインスタンス
sales_app = SalesManagementApp()
sales_app.setup_external_systems()

@app.route('/')
def index():
    """メインページ"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ログインページ"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if sales_app.login(user_id):
            session['user_id'] = user_id
            session['user_name'] = sales_app.current_user.name
            session['user_role'] = sales_app.current_user.role.value
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='無効なユーザーIDです')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """ログアウト"""
    session.clear()
    sales_app.logout()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """ダッシュボード"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/daily_reports')
def daily_reports():
    """日報管理ページ"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('daily_reports.html')

@app.route('/targets')
def targets():
    """目標管理ページ"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('targets.html')

@app.route('/products')
def products():
    """商品管理ページ"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('products.html')

@app.route('/analytics')
def analytics():
    """分析ページ"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('analytics.html')

@app.route('/team')
def team():
    """チーム管理ページ"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_role = session.get('user_role', 'sales')
    if user_role not in ['team_leader', 'manager', 'admin']:
        return redirect(url_for('dashboard'))
    
    return render_template('team.html')

# API エンドポイント
@app.route('/api/dashboard')
def api_dashboard():
    """ダッシュボードAPI"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    dashboard_data = sales_app.get_dashboard_data()
    return jsonify(dashboard_data)

@app.route('/api/reports', methods=['GET', 'POST'])
def api_reports():
    """日報API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'POST':
        if request.json.get('action') == 'create':
            result = sales_app.create_daily_report()
            return jsonify(result)
        elif request.json.get('action') == 'update':
            report_id = request.json.get('report_id')
            report_data = request.json.get('report_data', {})
            result = sales_app.update_daily_report(report_id, report_data)
            return jsonify(result)
        elif request.json.get('action') == 'submit':
            report_id = request.json.get('report_id')
            result = sales_app.submit_daily_report(report_id)
            return jsonify(result)
    
    # GET: 日報一覧取得
    user_id = session['user_id']
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    reports = sales_app.report_service.get_user_reports(user_id, start_date, end_date)
    
    reports_data = []
    for report in reports:
        reports_data.append({
            'report_id': report.report_id,
            'report_date': report.report_date.strftime('%Y-%m-%d'),
            'status': report.status,
            'working_hours': report.working_hours,
            'visits_count': len(report.visits),
            'sales_count': len(report.sales_results),
            'travel_expense': report.travel_expense
        })
    
    return jsonify({'reports': reports_data})

@app.route('/api/targets', methods=['GET', 'POST'])
def api_targets():
    """目標管理API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'POST':
        if request.json.get('action') == 'create':
            target_data = request.json.get('target_data', {})
            result = sales_app.create_target(target_data)
            return jsonify(result)
    
    # GET: 目標一覧取得
    user_id = session['user_id']
    current_targets = sales_app.target_service.get_current_targets(user_id)
    
    targets_data = []
    for target in current_targets:
        achievement_rate = sales_app.target_service.get_achievement_rate(target.target_id)
        targets_data.append({
            'target_id': target.target_id,
            'target_type': target.target_type.value,
            'target_value': target.target_value,
            'current_value': target.current_value,
            'achievement_rate': round(achievement_rate, 1),
            'period_start': target.period_start.strftime('%Y-%m-%d'),
            'period_end': target.period_end.strftime('%Y-%m-%d'),
            'description': target.description
        })
    
    return jsonify({'targets': targets_data})

@app.route('/api/products')
def api_products():
    """商品API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    products = sales_app.get_products_list()
    return jsonify({'products': products})

@app.route('/api/analytics')
def api_analytics():
    """分析API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    analytics_data = sales_app.get_target_analysis()
    return jsonify(analytics_data)

@app.route('/api/team')
def api_team():
    """チーム管理API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_role = session.get('user_role', 'sales')
    if user_role not in ['team_leader', 'manager', 'admin']:
        return jsonify({'error': 'Insufficient privileges'}), 403
    
    # サンプルチームデータ（実装簡略化）
    team_data = {
        'team_id': 't001',
        'team_name': '東京営業チーム',
        'members': [
            {'user_id': 'u001', 'name': '田中太郎', 'role': 'sales'},
            {'user_id': 'u002', 'name': '佐藤花子', 'role': 'sales'},
        ],
        'performance': {
            'total_sales': 2500000,
            'target_sales': 3000000,
            'achievement_rate': 83.3
        }
    }
    
    return jsonify(team_data)

@app.route('/api/sync')
def api_sync():
    """外部システム同期API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_role = session.get('user_role', 'sales')
    if user_role not in ['manager', 'admin']:
        return jsonify({'error': 'Insufficient privileges'}), 403
    
    sync_result = sales_app.sync_external_systems()
    return jsonify(sync_result)

@app.route('/api/export')
def api_export():
    """データエクスポートAPI"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    start_date = request.args.get('start_date', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    
    export_result = sales_app.export_reports(start_date, end_date)
    return jsonify(export_result)

# エラーハンドラー
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='ページが見つかりません'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='内部サーバーエラーが発生しました'), 500

if __name__ == '__main__':
    # テンプレートディレクトリとスタティックディレクトリを作成
    import os
    
    directories = ['templates', 'static/css', 'static/js', 'static/img']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # 環境変数からポート設定を取得（Heroku対応）
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info("営業管理Webアプリケーションを起動しています...")
    logger.info(f"アクセス先: http://{host}:{port}")
    
    app.run(debug=debug_mode, host=host, port=port)
