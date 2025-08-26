#!/usr/bin/env python3
"""
営業日報管理サービス
"""

from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
import logging
from models import DailyReport, Visit, SalesResult, User, Alert, AlertLevel
import json

logger = logging.getLogger(__name__)

class ReportService:
    """営業日報管理サービス"""
    
    def __init__(self):
        # 実際の実装ではデータベース接続を行う
        self.reports: Dict[str, DailyReport] = {}
        self.visits: Dict[str, Visit] = {}
        self.sales_results: Dict[str, SalesResult] = {}
        
    def create_daily_report(self, user_id: str, report_date: date) -> DailyReport:
        """日報を新規作成"""
        report_id = f"rpt_{user_id}_{report_date.strftime('%Y%m%d')}"
        
        # 既存チェック
        if report_id in self.reports:
            logger.warning(f"日報が既に存在します: {report_id}")
            return self.reports[report_id]
        
        report = DailyReport(
            report_id=report_id,
            user_id=user_id,
            report_date=report_date
        )
        
        self.reports[report_id] = report
        logger.info(f"新規日報作成: {report_id}")
        return report
    
    def update_daily_report(self, report_id: str, updates: Dict) -> bool:
        """日報を更新"""
        if report_id not in self.reports:
            logger.error(f"日報が見つかりません: {report_id}")
            return False
        
        report = self.reports[report_id]
        
        # 承認済みの日報は編集不可
        if report.status == "approved":
            logger.warning(f"承認済み日報は編集できません: {report_id}")
            return False
        
        # 更新可能フィールドのみ更新
        updatable_fields = [
            'activities', 'visits', 'sales_results', 'challenges', 
            'next_actions', 'working_hours', 'travel_expense'
        ]
        
        for field, value in updates.items():
            if field in updatable_fields:
                setattr(report, field, value)
        
        logger.info(f"日報更新完了: {report_id}")
        return True
    
    def submit_daily_report(self, report_id: str) -> bool:
        """日報を提出"""
        if report_id not in self.reports:
            logger.error(f"日報が見つかりません: {report_id}")
            return False
        
        report = self.reports[report_id]
        
        # バリデーション
        if not self._validate_report_for_submission(report):
            return False
        
        report.status = "submitted"
        report.submitted_at = datetime.now()
        
        logger.info(f"日報提出完了: {report_id}")
        return True
    
    def approve_daily_report(self, report_id: str, approver_id: str) -> bool:
        """日報を承認"""
        if report_id not in self.reports:
            logger.error(f"日報が見つかりません: {report_id}")
            return False
        
        report = self.reports[report_id]
        
        if report.status != "submitted":
            logger.warning(f"提出済み日報のみ承認可能です: {report_id}")
            return False
        
        report.status = "approved"
        report.approved_at = datetime.now()
        report.approved_by = approver_id
        
        logger.info(f"日報承認完了: {report_id} by {approver_id}")
        return True
    
    def get_user_reports(self, user_id: str, start_date: date, end_date: date) -> List[DailyReport]:
        """ユーザーの日報一覧を取得"""
        user_reports = []
        
        for report in self.reports.values():
            if (report.user_id == user_id and 
                start_date <= report.report_date <= end_date):
                user_reports.append(report)
        
        return sorted(user_reports, key=lambda x: x.report_date, reverse=True)
    
    def get_pending_approvals(self, approver_id: str) -> List[DailyReport]:
        """承認待ち日報一覧を取得"""
        pending_reports = []
        
        for report in self.reports.values():
            if report.status == "submitted":
                # 実際の実装では承認者の権限チェックを行う
                pending_reports.append(report)
        
        return sorted(pending_reports, key=lambda x: x.submitted_at)
    
    def add_visit_record(self, visit: Visit) -> bool:
        """訪問記録を追加"""
        self.visits[visit.visit_id] = visit
        
        # 対応する日報に訪問記録を追加
        report_id = f"rpt_{visit.user_id}_{visit.visit_date.date().strftime('%Y%m%d')}"
        if report_id in self.reports:
            visit_data = {
                "visit_id": visit.visit_id,
                "customer_id": visit.customer_id,
                "time": visit.visit_date.strftime("%H:%M"),
                "purpose": visit.purpose,
                "outcome": visit.outcome
            }
            self.reports[report_id].visits.append(visit_data)
        
        logger.info(f"訪問記録追加: {visit.visit_id}")
        return True
    
    def add_sales_result(self, sales_result: SalesResult) -> bool:
        """販売実績を追加"""
        self.sales_results[sales_result.result_id] = sales_result
        
        # 対応する日報に販売実績を追加
        report_id = f"rpt_{sales_result.user_id}_{sales_result.sale_date.strftime('%Y%m%d')}"
        if report_id in self.reports:
            sales_data = {
                "result_id": sales_result.result_id,
                "customer_id": sales_result.customer_id,
                "product_id": sales_result.product_id,
                "quantity": sales_result.quantity,
                "amount": sales_result.total_amount
            }
            self.reports[report_id].sales_results.append(sales_data)
        
        logger.info(f"販売実績追加: {sales_result.result_id}")
        return True
    
    def get_report_statistics(self, user_id: str, period_days: int = 30) -> Dict:
        """日報統計情報を取得"""
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        
        user_reports = self.get_user_reports(user_id, start_date, end_date)
        
        stats = {
            "total_reports": len(user_reports),
            "submitted_reports": sum(1 for r in user_reports if r.status in ["submitted", "approved"]),
            "approved_reports": sum(1 for r in user_reports if r.status == "approved"),
            "total_visits": sum(len(r.visits) for r in user_reports),
            "total_sales": sum(len(r.sales_results) for r in user_reports),
            "total_working_hours": sum(r.working_hours for r in user_reports),
            "total_travel_expense": sum(r.travel_expense for r in user_reports),
            "submission_rate": 0
        }
        
        if stats["total_reports"] > 0:
            stats["submission_rate"] = (stats["submitted_reports"] / stats["total_reports"]) * 100
        
        return stats
    
    def generate_missing_report_alerts(self) -> List[Alert]:
        """日報未提出アラートを生成"""
        alerts = []
        yesterday = date.today() - timedelta(days=1)
        
        # 実際の実装では全ユーザーをDBから取得
        # ここではサンプル用の簡略化
        sample_users = ["u001", "u002"]  
        
        for user_id in sample_users:
            report_id = f"rpt_{user_id}_{yesterday.strftime('%Y%m%d')}"
            
            if report_id not in self.reports or self.reports[report_id].status == "draft":
                alert = Alert(
                    alert_id=f"alert_missing_{user_id}_{yesterday.strftime('%Y%m%d')}",
                    user_id=user_id,
                    alert_type="missing_report",
                    level=AlertLevel.WARNING,
                    title="日報未提出",
                    message=f"{yesterday.strftime('%Y年%m月%d日')}の日報が未提出です。",
                    expires_at=datetime.now() + timedelta(days=7)
                )
                alerts.append(alert)
        
        return alerts
    
    def _validate_report_for_submission(self, report: DailyReport) -> bool:
        """日報提出前バリデーション"""
        errors = []
        
        # 必須項目チェック
        if not report.activities:
            errors.append("活動内容が入力されていません")
        
        if report.working_hours <= 0:
            errors.append("労働時間が入力されていません")
        
        if report.working_hours > 24:
            errors.append("労働時間が不正です（24時間を超えています）")
        
        if errors:
            logger.warning(f"日報バリデーションエラー {report.report_id}: {', '.join(errors)}")
            return False
        
        return True
    
    def export_reports_to_csv(self, user_id: str, start_date: date, end_date: date) -> str:
        """日報をCSV形式でエクスポート"""
        reports = self.get_user_reports(user_id, start_date, end_date)
        
        csv_lines = ["日付,労働時間,訪問件数,売上件数,交通費,状況"]
        
        for report in reports:
            line = f"{report.report_date},{report.working_hours},{len(report.visits)},{len(report.sales_results)},{report.travel_expense},{report.status}"
            csv_lines.append(line)
        
        return "\n".join(csv_lines)

# 使用例とテスト用のメイン関数
def main():
    """テスト用メイン関数"""
    logger.info("営業日報サービス初期化開始...")
    
    service = ReportService()
    
    # サンプル日報作成
    today = date.today()
    report = service.create_daily_report("u001", today)
    
    # 日報更新
    updates = {
        "activities": [
            {"time": "09:00", "activity": "顧客A社訪問", "detail": "新商品提案"},
            {"time": "14:00", "activity": "資料作成", "detail": "提案書作成"}
        ],
        "working_hours": 8.0,
        "travel_expense": 1200,
        "challenges": "競合他社の価格競争が激化",
        "next_actions": "価格見直しの検討、上司への相談"
    }
    
    service.update_daily_report(report.report_id, updates)
    
    # 統計情報取得
    stats = service.get_report_statistics("u001")
    logger.info(f"統計情報: {stats}")
    
    # 日報提出
    service.submit_daily_report(report.report_id)
    
    logger.info("営業日報サービステスト完了")

if __name__ == "__main__":
    main()
