#!/usr/bin/env python3
"""
システム設定ファイル
"""

import os
from datetime import timedelta
from typing import Dict, Any

class Config:
    """基本設定クラス"""
    
    # アプリケーション基本設定
    APP_NAME = "空気清浄機販売営業管理システム"
    VERSION = "1.0.0"
    DEBUG = True
    
    # データベース設定（将来的なDB化用）
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///sales_management.db')
    
    # ログ設定
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # セキュリティ設定
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    JWT_EXPIRATION_DELTA = timedelta(hours=8)
    
    # 外部システム連携設定
    EXTERNAL_API_TIMEOUT = int(os.environ.get('EXTERNAL_API_TIMEOUT', '30'))
    MAX_RETRY_ATTEMPTS = int(os.environ.get('MAX_RETRY_ATTEMPTS', '3'))
    
    # アラート設定
    ALERT_SETTINGS = {
        "missing_report_hours": 24,  # 日報未提出アラートまでの時間
        "target_warning_threshold": 50,  # 目標達成率警告閾値（%）
        "deadline_warning_days": 3,  # 期限前警告日数
        "critical_achievement_rate": 30,  # 重要アラート閾値（%）
    }
    
    # 目標管理設定
    TARGET_SETTINGS = {
        "default_weights": {
            "skill": 0.4,
            "experience": 0.25,
            "culture": 0.20,
            "education": 0.15
        },
        "achievement_rates": {
            "excellent": 100,
            "good": 80,
            "average": 60,
            "poor": 40
        }
    }
    
    # レポート設定
    REPORT_SETTINGS = {
        "max_working_hours": 12,
        "default_working_hours": 8,
        "max_travel_expense": 10000,
        "export_formats": ["csv", "pdf", "excel"]
    }

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    
class TestConfig(Config):
    """テスト環境設定"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# 環境別設定の辞書
config_dict: Dict[str, Any] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig
}

def get_config(env: str = None) -> Config:
    """環境設定を取得"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    return config_dict.get(env, DevelopmentConfig)()
