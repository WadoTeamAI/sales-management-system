#!/usr/bin/env python3
"""
空気清浄機販売営業向け日報・目標管理システム - メインアプリケーション
"""

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
import logging
import json
from dataclasses import asdict

# 各サービスをインポート
from models import (
    User, UserRole, Target, TargetType, DailyReport, 
    Product, ProductCategory, Customer, Alert, AlertLevel,
    create_sample_data
)
from report_service import ReportService
from target_service import TargetService
from integration_service import IntegrationService, ExternalSystemConfig

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SalesManagementApp:
    """営業管理アプリケーション メインクラス"""
    
    def __init__(self):
        # 各サービスを初期化
        self.report_service = ReportService()
        self.target_service = TargetService()
        self.integration_service = IntegrationService()
        
        # ユーザーセッション管理
        self.current_user: Optional[User] = None
        self.users: Dict[str, User] = {}
        self.products: Dict[str, Product] = {}
        self.customers: Dict[str, Customer] = {}
        
        # 初期データロード
        self._load_initial_data()
        
        logger.info("営業管理アプリケーション初期化完了")
    
    def _load_initial_data(self):
        """初期データをロード"""
        sample_data = create_sample_data()
        
        # ユーザーデータ
        for user in sample_data["users"]:
            self.users[user.user_id] = user
        
        # 商品データ
        for product in sample_data["products"]:
            self.products[product.product_id] = product
        
        logger.info(f"初期データロード完了: ユーザー{len(self.users)}名、商品{len(self.products)}点")
    
    def login(self, user_id: str) -> bool:
        """ユーザーログイン"""
        if user_id in self.users:
            self.current_user = self.users[user_id]
            logger.info(f"ユーザーログイン: {self.current_user.name}")
            return True
        
        logger.error(f"存在しないユーザー: {user_id}")
        return False
    
    def logout(self):
        """ユーザーログアウト"""
        if self.current_user:
            logger.info(f"ユーザーログアウト: {self.current_user.name}")
            self.current_user = None
    
    def get_dashboard_data(self) -> Dict:
        """ダッシュボードデータを取得"""
        if not self.current_user:
            return {"error": "ログインが必要です"}
        
        user_id = self.current_user.user_id
        
        # 日報統計
        report_stats = self.report_service.get_report_statistics(user_id)
        
        # 目標サマリー
        target_summary = self.target_service.get_target_summary(user_id)
        
        # アラート取得
        report_alerts = self.report_service.generate_missing_report_alerts()
        target_alerts = self.target_service.generate_target_alerts(user_id)
        all_alerts = report_alerts + target_alerts
        
        # 最近の活動
        today = date.today()
        recent_reports = self.report_service.get_user_reports(
            user_id, today - timedelta(days=7), today
        )
        
        dashboard_data = {
            "user_info": {
                "name": self.current_user.name,
                "role": self.current_user.role.value,
                "team_id": self.current_user.team_id
            },
            "report_statistics": report_stats,
            "target_summary": target_summary,
            "alerts": [
                {
                    "id": alert.alert_id,
                    "type": alert.alert_type,
                    "level": alert.level.value,
                    "title": alert.title,
                    "message": alert.message,
                    "created_at": alert.created_at.strftime("%Y-%m-%d %H:%M")
                }
                for alert in all_alerts[:5]  # 最新5件のみ
            ],
            "recent_activities": [
                {
                    "date": report.report_date.strftime("%Y-%m-%d"),
                    "status": report.status,
                    "visits_count": len(report.visits),
                    "sales_count": len(report.sales_results)
                }
                for report in recent_reports[:5]
            ]
        }
        
        return dashboard_data
    
    def create_daily_report(self, report_date: Optional[date] = None) -> Dict:
        """日報作成"""
        if not self.current_user:
            return {"error": "ログインが必要です"}
        
        if not report_date:
            report_date = date.today()
        
        report = self.report_service.create_daily_report(
            self.current_user.user_id, report_date
        )
        
        return {
            "success": True,
            "report_id": report.report_id,
            "message": "日報を作成しました"
        }
    
    def update_daily_report(self, report_id: str, report_data: Dict) -> Dict:
        """日報更新"""
        if not self.current_user:
            return {"error": "ログインが必要です"}
        
        success = self.report_service.update_daily_report(report_id, report_data)
        
        if success:
            return {"success": True, "message": "日報を更新しました"}
        else:
            return {"error": "日報の更新に失敗しました"}
    
    def submit_daily_report(self, report_id: str) -> Dict:
        """日報提出"""
        if not self.current_user:
            return {"error": "ログインが必要です"}
        
        success = self.report_service.submit_daily_report(report_id)
        
        if success:
            # CRMシステムに同期
            report = self.report_service.reports.get(report_id)
            if report:
                report_data = asdict(report)
                self.integration_service.push_daily_report_to_crm(report_data)
            
            return {"success": True, "message": "日報を提出しました"}
        else:
            return {"error": "日報の提出に失敗しました"}
    
    def create_target(self, target_data: Dict) -> Dict:
        """目標作成"""
        if not self.current_user:
            return {"error": "ログインが必要です"}
        
        try:
            target = self.target_service.create_target(
                user_id=self.current_user.user_id,
                target_type=TargetType(target_data["target_type"]),
                period_start=datetime.strptime(target_data["period_start"], "%Y-%m-%d").date(),
                period_end=datetime.strptime(target_data["period_end"], "%Y-%m-%d").date(),
                target_value=float(target_data["target_value"]),
                product_id=target_data.get("product_id"),
                description=target_data.get("description", "")
            )
            
            return {
                "success": True,
                "target_id": target.target_id,
                "message": "目標を作成しました"
            }
            
        except Exception as e:
            logger.error(f"目標作成エラー: {str(e)}")
            return {"error": f"目標の作成に失敗しました: {str(e)}"}
    
    def get_target_analysis(self) -> Dict:
        """目標分析データを取得"""
        if not self.current_user:
            return {"error": "ログインが必要です"}
        
        # 進捗更新
        self.target_service.update_target_progress(self.current_user.user_id)
        
        # ギャップ分析
        gap_analysis = self.target_service.analyze_target_gaps(self.current_user.user_id)
        
        return {
            "gap_analysis": {
                "charts_data": gap_analysis.charts_data,
                "insights": gap_analysis.insights,
                "recommendations": gap_analysis.recommendations,
                "metrics": gap_analysis.metrics
            }
        }
    
    def get_products_list(self) -> List[Dict]:
        """商品一覧取得"""
        return [
            {
                "product_id": product.product_id,
                "product_name": product.product_name,
                "model_number": product.model_number,
                "category": product.category.value,
                "price": product.price,
                "stock_quantity": product.stock_quantity,
                "specifications": product.specifications
            }
            for product in self.products.values()
            if product.is_active
        ]
    
    def sync_external_systems(self) -> Dict:
        """外部システム同期"""
        if not self.current_user:
            return {"error": "ログインが必要です"}
        
        # 管理者権限チェック
        if self.current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            return {"error": "権限がありません"}
        
        sync_results = self.integration_service.sync_all_systems()
        
        return {
            "success": True,
            "sync_results": sync_results,
            "message": "外部システム同期を実行しました"
        }
    
    def get_team_performance(self, team_id: str) -> Dict:
        """チーム成績取得"""
        if not self.current_user:
            return {"error": "ログインが必要です"}
        
        # チームリーダー以上の権限チェック
        if self.current_user.role not in [UserRole.TEAM_LEADER, UserRole.MANAGER, UserRole.ADMIN]:
            return {"error": "権限がありません"}
        
        # チームメンバー取得（実装簡略化）
        team_members = [user_id for user_id, user in self.users.items() 
                       if user.team_id == team_id]
        
        team_summary = self.target_service.get_team_target_summary(team_id, team_members)
        
        return {
            "success": True,
            "team_summary": team_summary
        }
    
    def export_reports(self, start_date: str, end_date: str) -> Dict:
        """日報エクスポート"""
        if not self.current_user:
            return {"error": "ログインが必要です"}
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            csv_content = self.report_service.export_reports_to_csv(
                self.current_user.user_id, start, end
            )
            
            return {
                "success": True,
                "csv_content": csv_content,
                "filename": f"reports_{self.current_user.user_id}_{start_date}_to_{end_date}.csv"
            }
            
        except Exception as e:
            logger.error(f"エクスポートエラー: {str(e)}")
            return {"error": f"エクスポートに失敗しました: {str(e)}"}
    
    def setup_external_systems(self):
        """外部システムセットアップ"""
        # サンプル CRM設定
        crm_config = ExternalSystemConfig(
            config_id="crm_main",
            system_name="営業CRM",
            system_type="crm",
            api_endpoint="https://api.ourcrm.com/v1",
            api_key="your_crm_api_key",
            sync_frequency="daily",
            is_active=False  # 初期は無効
        )
        
        # サンプル 会計ソフト設定
        accounting_config = ExternalSystemConfig(
            config_id="accounting_main",
            system_name="会計ソフト",
            system_type="accounting",
            api_endpoint="https://api.ouraccounting.com/v1",
            api_key="your_accounting_api_key",
            sync_frequency="daily",
            is_active=False  # 初期は無効
        )
        
        self.integration_service.register_system(crm_config)
        self.integration_service.register_system(accounting_config)
        
        logger.info("外部システム設定完了（実際の連携には設定変更が必要）")

def main():
    """メイン処理"""
    print("="*60)
    print("空気清浄機販売営業向け日報・目標管理システム")
    print("="*60)
    
    # アプリケーション初期化
    app = SalesManagementApp()
    app.setup_external_systems()
    
    # サンプルユーザーでログイン
    if app.login("u001"):  # 田中太郎でログイン
        
        # ダッシュボードデータ取得
        dashboard = app.get_dashboard_data()
        print(f"\n【ダッシュボード】")
        print(f"ユーザー: {dashboard['user_info']['name']} ({dashboard['user_info']['role']})")
        print(f"日報統計: 提出率 {dashboard['report_statistics']['submission_rate']:.1f}%")
        print(f"目標サマリー: 総目標数 {dashboard['target_summary']['total_targets']}件")
        print(f"アラート: {len(dashboard['alerts'])}件")
        
        # 日報作成テスト
        report_result = app.create_daily_report()
        if report_result.get("success"):
            print(f"\n【日報作成】{report_result['message']}")
            
            # 日報更新
            sample_report_data = {
                "activities": [
                    {"time": "09:00", "activity": "A社訪問", "detail": "新商品エアクリーンPro提案"},
                    {"time": "14:00", "activity": "見積書作成", "detail": "B社向け提案書"}
                ],
                "working_hours": 8.0,
                "travel_expense": 1500,
                "challenges": "競合他社の価格攻勢が厳しい状況",
                "next_actions": "価格見直しと上司相談を実施"
            }
            
            update_result = app.update_daily_report(report_result["report_id"], sample_report_data)
            if update_result.get("success"):
                print(f"【日報更新】{update_result['message']}")
        
        # 目標作成テスト
        target_data = {
            "target_type": "sales_amount",
            "period_start": "2024-04-01",
            "period_end": "2024-04-30",
            "target_value": 1500000,  # 150万円
            "description": "4月売上目標"
        }
        
        target_result = app.create_target(target_data)
        if target_result.get("success"):
            print(f"\n【目標作成】{target_result['message']}")
        
        # 商品一覧表示
        products = app.get_products_list()
        print(f"\n【商品一覧】{len(products)}点の商品を管理中")
        for product in products:
            print(f"  - {product['product_name']} (¥{product['price']:,})")
        
        # ログアウト
        app.logout()
    
    print("\n" + "="*60)
    print("システムデモ完了")
    print("="*60)

if __name__ == "__main__":
    main()
