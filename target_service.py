#!/usr/bin/env python3
"""
目標管理サービス
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
from models import Target, TargetType, SalesResult, Alert, AlertLevel, AnalyticsResult
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

class TargetService:
    """目標管理サービス"""
    
    def __init__(self):
        # 実際の実装ではデータベース接続を行う
        self.targets: Dict[str, Target] = {}
        self.sales_results: Dict[str, SalesResult] = {}
        
    def create_target(self, user_id: str, target_type: TargetType, 
                     period_start: date, period_end: date, 
                     target_value: float, product_id: Optional[str] = None,
                     description: str = "") -> Target:
        """目標を新規作成"""
        target_id = f"tgt_{user_id}_{target_type.value}_{period_start.strftime('%Y%m%d')}"
        
        # 商品別目標の場合はproduct_idを含める
        if product_id:
            target_id = f"{target_id}_{product_id}"
        
        # 既存の重複目標チェック
        if target_id in self.targets:
            logger.warning(f"目標が既に存在します: {target_id}")
            return self.targets[target_id]
        
        target = Target(
            target_id=target_id,
            user_id=user_id,
            target_type=target_type,
            period_start=period_start,
            period_end=period_end,
            target_value=target_value,
            product_id=product_id,
            description=description
        )
        
        self.targets[target_id] = target
        logger.info(f"新規目標作成: {target_id}")
        return target
    
    def update_target(self, target_id: str, updates: Dict) -> bool:
        """目標を更新"""
        if target_id not in self.targets:
            logger.error(f"目標が見つかりません: {target_id}")
            return False
        
        target = self.targets[target_id]
        
        # 更新可能フィールド
        updatable_fields = ['target_value', 'description', 'period_end']
        
        for field, value in updates.items():
            if field in updatable_fields:
                setattr(target, field, value)
        
        logger.info(f"目標更新完了: {target_id}")
        return True
    
    def deactivate_target(self, target_id: str) -> bool:
        """目標を無効化"""
        if target_id not in self.targets:
            logger.error(f"目標が見つかりません: {target_id}")
            return False
        
        self.targets[target_id].is_active = False
        logger.info(f"目標無効化: {target_id}")
        return True
    
    def get_user_targets(self, user_id: str, active_only: bool = True) -> List[Target]:
        """ユーザーの目標一覧を取得"""
        user_targets = []
        
        for target in self.targets.values():
            if target.user_id == user_id:
                if not active_only or target.is_active:
                    user_targets.append(target)
        
        return sorted(user_targets, key=lambda x: x.created_at, reverse=True)
    
    def get_current_targets(self, user_id: str) -> List[Target]:
        """現在進行中の目標を取得"""
        today = date.today()
        current_targets = []
        
        for target in self.targets.values():
            if (target.user_id == user_id and 
                target.is_active and
                target.period_start <= today <= target.period_end):
                current_targets.append(target)
        
        return current_targets
    
    def update_target_progress(self, user_id: str) -> Dict[str, int]:
        """目標進捗を更新"""
        updated_count = 0
        current_targets = self.get_current_targets(user_id)
        
        for target in current_targets:
            old_value = target.current_value
            new_value = self._calculate_current_value(target)
            
            if new_value != old_value:
                target.current_value = new_value
                updated_count += 1
        
        logger.info(f"目標進捗更新完了: {user_id} ({updated_count}件)")
        return {"updated_targets": updated_count}
    
    def _calculate_current_value(self, target: Target) -> float:
        """目標の現在値を計算"""
        current_value = 0.0
        
        for sales_result in self.sales_results.values():
            if (sales_result.user_id == target.user_id and
                target.period_start <= sales_result.sale_date <= target.period_end):
                
                # 商品別目標の場合は商品IDも一致する必要がある
                if target.product_id and sales_result.product_id != target.product_id:
                    continue
                
                if target.target_type == TargetType.SALES_AMOUNT:
                    current_value += sales_result.total_amount
                elif target.target_type == TargetType.PROFIT:
                    current_value += sales_result.profit_amount
                elif target.target_type == TargetType.QUANTITY:
                    current_value += sales_result.quantity
        
        return current_value
    
    def get_achievement_rate(self, target_id: str) -> float:
        """達成率を計算"""
        if target_id not in self.targets:
            return 0.0
        
        target = self.targets[target_id]
        
        if target.target_value == 0:
            return 100.0 if target.current_value > 0 else 0.0
        
        return (target.current_value / target.target_value) * 100
    
    def get_target_summary(self, user_id: str) -> Dict:
        """目標サマリー情報を取得"""
        current_targets = self.get_current_targets(user_id)
        
        summary = {
            "total_targets": len(current_targets),
            "achieved_targets": 0,
            "behind_targets": 0,
            "on_track_targets": 0,
            "critical_targets": 0,
            "targets_by_type": defaultdict(int),
            "average_achievement_rate": 0.0
        }
        
        total_achievement = 0.0
        
        for target in current_targets:
            achievement_rate = self.get_achievement_rate(target.target_id)
            total_achievement += achievement_rate
            
            # 目標分類
            if achievement_rate >= 100:
                summary["achieved_targets"] += 1
            elif achievement_rate >= 80:
                summary["on_track_targets"] += 1
            elif achievement_rate >= 50:
                summary["behind_targets"] += 1
            else:
                summary["critical_targets"] += 1
            
            # タイプ別集計
            summary["targets_by_type"][target.target_type.value] += 1
        
        if current_targets:
            summary["average_achievement_rate"] = total_achievement / len(current_targets)
        
        return summary
    
    def generate_target_alerts(self, user_id: str) -> List[Alert]:
        """目標関連のアラートを生成"""
        alerts = []
        current_targets = self.get_current_targets(user_id)
        today = date.today()
        
        for target in current_targets:
            achievement_rate = self.get_achievement_rate(target.target_id)
            days_left = (target.period_end - today).days
            
            # 期限切れアラート
            if days_left < 0:
                alert = Alert(
                    alert_id=f"alert_expired_{target.target_id}",
                    user_id=user_id,
                    alert_type="target_expired",
                    level=AlertLevel.CRITICAL,
                    title="目標期限超過",
                    message=f"{target.target_type.value}目標の期限が{abs(days_left)}日超過しています。",
                    target_id=target.target_id
                )
                alerts.append(alert)
            
            # 達成率低下アラート
            elif achievement_rate < 50 and days_left <= 7:
                alert = Alert(
                    alert_id=f"alert_low_achievement_{target.target_id}",
                    user_id=user_id,
                    alert_type="low_achievement",
                    level=AlertLevel.WARNING,
                    title="目標達成率低下",
                    message=f"{target.target_type.value}目標の達成率が{achievement_rate:.1f}%です（残り{days_left}日）。",
                    target_id=target.target_id
                )
                alerts.append(alert)
            
            # 期限間近アラート
            elif days_left <= 3:
                alert = Alert(
                    alert_id=f"alert_deadline_{target.target_id}",
                    user_id=user_id,
                    alert_type="target_deadline",
                    level=AlertLevel.INFO,
                    title="目標期限間近",
                    message=f"{target.target_type.value}目標の期限まで{days_left}日です。",
                    target_id=target.target_id
                )
                alerts.append(alert)
        
        return alerts
    
    def analyze_target_gaps(self, user_id: str) -> AnalyticsResult:
        """目標と実績のギャップ分析"""
        current_targets = self.get_current_targets(user_id)
        today = date.today()
        
        analysis = AnalyticsResult(
            analysis_id=f"gap_analysis_{user_id}_{today.strftime('%Y%m%d')}",
            user_id=user_id,
            analysis_type="target_gap_analysis",
            period_start=today,
            period_end=today
        )
        
        gap_data = []
        insights = []
        recommendations = []
        
        for target in current_targets:
            achievement_rate = self.get_achievement_rate(target.target_id)
            gap_amount = target.target_value - target.current_value
            days_left = (target.period_end - today).days
            
            gap_info = {
                "target_type": target.target_type.value,
                "target_value": target.target_value,
                "current_value": target.current_value,
                "gap_amount": gap_amount,
                "achievement_rate": achievement_rate,
                "days_left": days_left,
                "daily_required": gap_amount / max(days_left, 1) if gap_amount > 0 else 0
            }
            gap_data.append(gap_info)
            
            # インサイト生成
            if achievement_rate < 50:
                insights.append(f"{target.target_type.value}目標の達成率が大幅に低下しています（{achievement_rate:.1f}%）")
            elif achievement_rate > 100:
                insights.append(f"{target.target_type.value}目標を達成しました！素晴らしい成果です")
            
            # 推奨アクション生成
            if gap_amount > 0 and days_left > 0:
                if target.target_type == TargetType.SALES_AMOUNT:
                    recommendations.append(f"売上目標達成には1日あたり{gap_info['daily_required']:,.0f}円の売上が必要です")
                elif target.target_type == TargetType.QUANTITY:
                    recommendations.append(f"販売数量目標達成には1日あたり{gap_info['daily_required']:.1f}個の販売が必要です")
        
        analysis.charts_data = {"gap_analysis": gap_data}
        analysis.insights = insights
        analysis.recommendations = recommendations
        
        # メトリクス設定
        if gap_data:
            analysis.metrics = {
                "total_targets": len(gap_data),
                "average_achievement_rate": sum(d["achievement_rate"] for d in gap_data) / len(gap_data),
                "targets_behind_schedule": sum(1 for d in gap_data if d["achievement_rate"] < 80)
            }
        
        return analysis
    
    def get_team_target_summary(self, team_id: str, user_ids: List[str]) -> Dict:
        """チーム目標サマリーを取得"""
        team_summary = {
            "team_id": team_id,
            "total_members": len(user_ids),
            "members_summary": {},
            "team_totals": defaultdict(float),
            "team_targets": defaultdict(float),
            "team_achievement_rates": {}
        }
        
        for user_id in user_ids:
            user_targets = self.get_current_targets(user_id)
            user_summary = self.get_target_summary(user_id)
            
            team_summary["members_summary"][user_id] = user_summary
            
            # チーム合計計算
            for target in user_targets:
                target_type = target.target_type.value
                team_summary["team_totals"][target_type] += target.current_value
                team_summary["team_targets"][target_type] += target.target_value
        
        # チーム達成率計算
        for target_type, total_target in team_summary["team_targets"].items():
            if total_target > 0:
                current_total = team_summary["team_totals"][target_type]
                team_summary["team_achievement_rates"][target_type] = (current_total / total_target) * 100
        
        return team_summary

# テスト用のメイン関数
def main():
    """テスト用メイン関数"""
    logger.info("目標管理サービス初期化開始...")
    
    service = TargetService()
    
    # サンプル目標作成
    today = date.today()
    month_end = date(today.year, today.month + 1, 1) - timedelta(days=1) if today.month < 12 else date(today.year, 12, 31)
    
    # 売上目標
    sales_target = service.create_target(
        user_id="u001",
        target_type=TargetType.SALES_AMOUNT,
        period_start=date(today.year, today.month, 1),
        period_end=month_end,
        target_value=1000000,  # 100万円
        description="月次売上目標"
    )
    
    # 商品別販売数量目標
    product_target = service.create_target(
        user_id="u001",
        target_type=TargetType.QUANTITY,
        period_start=date(today.year, today.month, 1),
        period_end=month_end,
        target_value=10,  # 10台
        product_id="p001",
        description="エアクリーン Pro 販売目標"
    )
    
    # サンプル販売実績追加（テスト用）
    sales_result = SalesResult(
        result_id="sr001",
        user_id="u001",
        customer_id="c001",
        product_id="p001",
        quantity=2,
        unit_price=59800,
        total_amount=119600,
        profit_amount=49600,
        sale_date=today
    )
    service.sales_results[sales_result.result_id] = sales_result
    
    # 進捗更新
    service.update_target_progress("u001")
    
    # 達成率計算
    sales_rate = service.get_achievement_rate(sales_target.target_id)
    product_rate = service.get_achievement_rate(product_target.target_id)
    
    logger.info(f"売上目標達成率: {sales_rate:.1f}%")
    logger.info(f"商品販売目標達成率: {product_rate:.1f}%")
    
    # サマリー取得
    summary = service.get_target_summary("u001")
    logger.info(f"目標サマリー: {summary}")
    
    # ギャップ分析
    gap_analysis = service.analyze_target_gaps("u001")
    logger.info(f"ギャップ分析完了: {len(gap_analysis.insights)}件のインサイト")
    
    logger.info("目標管理サービステスト完了")

if __name__ == "__main__":
    main()
