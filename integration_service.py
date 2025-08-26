#!/usr/bin/env python3
"""
外部システム連携サービス
CRM・会計ソフトとの連携機能
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import logging
import requests
import json
from models import ExternalSystemConfig, Customer, SalesResult, Product
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ExternalSystemConnector(ABC):
    """外部システム連携の基底クラス"""
    
    def __init__(self, config: ExternalSystemConfig):
        self.config = config
    
    @abstractmethod
    def test_connection(self) -> bool:
        """接続テスト"""
        pass
    
    @abstractmethod
    def sync_data(self) -> Dict[str, Any]:
        """データ同期"""
        pass

class CRMConnector(ExternalSystemConnector):
    """CRMシステム連携"""
    
    def __init__(self, config: ExternalSystemConfig):
        super().__init__(config)
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> bool:
        """CRM接続テスト"""
        try:
            response = requests.get(
                f"{self.config.api_endpoint}/health",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"CRM接続成功: {self.config.system_name}")
                return True
            else:
                logger.error(f"CRM接続エラー: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"CRM接続例外: {str(e)}")
            return False
    
    def sync_customers(self) -> List[Customer]:
        """顧客情報同期"""
        try:
            response = requests.get(
                f"{self.config.api_endpoint}/customers",
                headers=self.headers,
                params={"updated_since": self.config.last_sync.isoformat() if self.config.last_sync else None}
            )
            
            if response.status_code == 200:
                customers_data = response.json()
                customers = []
                
                for customer_data in customers_data.get("customers", []):
                    customer = Customer(
                        customer_id=customer_data["id"],
                        company_name=customer_data["company_name"],
                        contact_person=customer_data["contact_person"],
                        email=customer_data["email"],
                        phone=customer_data["phone"],
                        address=customer_data["address"],
                        industry=customer_data.get("industry", ""),
                        customer_type=customer_data.get("customer_type", "existing")
                    )
                    customers.append(customer)
                
                logger.info(f"CRM顧客情報同期完了: {len(customers)}件")
                return customers
            
            else:
                logger.error(f"顧客情報取得エラー: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"顧客情報同期例外: {str(e)}")
            return []
    
    def push_sales_activity(self, activity_data: Dict) -> bool:
        """営業活動をCRMにプッシュ"""
        try:
            response = requests.post(
                f"{self.config.api_endpoint}/activities",
                headers=self.headers,
                json=activity_data
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"営業活動プッシュ成功: {activity_data.get('activity_id')}")
                return True
            else:
                logger.error(f"営業活動プッシュエラー: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"営業活動プッシュ例外: {str(e)}")
            return False
    
    def sync_data(self) -> Dict[str, Any]:
        """CRMデータ同期"""
        result = {
            "success": False,
            "customers_synced": 0,
            "activities_pushed": 0,
            "errors": []
        }
        
        try:
            # 顧客情報同期
            customers = self.sync_customers()
            result["customers_synced"] = len(customers)
            
            # 同期時刻更新
            self.config.last_sync = datetime.now()
            result["success"] = True
            
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"CRMデータ同期エラー: {str(e)}")
        
        return result

class AccountingConnector(ExternalSystemConnector):
    """会計ソフト連携"""
    
    def __init__(self, config: ExternalSystemConfig):
        super().__init__(config)
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> bool:
        """会計ソフト接続テスト"""
        try:
            response = requests.get(
                f"{self.config.api_endpoint}/status",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"会計ソフト接続成功: {self.config.system_name}")
                return True
            else:
                logger.error(f"会計ソフト接続エラー: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"会計ソフト接続例外: {str(e)}")
            return False
    
    def sync_sales_data(self) -> List[SalesResult]:
        """売上データ同期"""
        try:
            since_date = self.config.last_sync.strftime("%Y-%m-%d") if self.config.last_sync else (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            response = requests.get(
                f"{self.config.api_endpoint}/sales",
                headers=self.headers,
                params={
                    "since": since_date,
                    "status": "confirmed"
                }
            )
            
            if response.status_code == 200:
                sales_data = response.json()
                sales_results = []
                
                for sale_data in sales_data.get("sales", []):
                    sales_result = SalesResult(
                        result_id=sale_data["id"],
                        user_id=sale_data.get("sales_person_id", "unknown"),
                        customer_id=sale_data["customer_id"],
                        product_id=sale_data["product_id"],
                        quantity=sale_data["quantity"],
                        unit_price=sale_data["unit_price"],
                        total_amount=sale_data["total_amount"],
                        profit_amount=sale_data.get("profit_amount", 0),
                        sale_date=datetime.strptime(sale_data["sale_date"], "%Y-%m-%d").date(),
                        status=sale_data.get("status", "contracted")
                    )
                    sales_results.append(sales_result)
                
                logger.info(f"会計ソフト売上データ同期完了: {len(sales_results)}件")
                return sales_results
            
            else:
                logger.error(f"売上データ取得エラー: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"売上データ同期例外: {str(e)}")
            return []
    
    def push_expense_data(self, expense_data: Dict) -> bool:
        """経費データを会計ソフトにプッシュ"""
        try:
            response = requests.post(
                f"{self.config.api_endpoint}/expenses",
                headers=self.headers,
                json=expense_data
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"経費データプッシュ成功: {expense_data.get('expense_id')}")
                return True
            else:
                logger.error(f"経費データプッシュエラー: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"経費データプッシュ例外: {str(e)}")
            return False
    
    def sync_data(self) -> Dict[str, Any]:
        """会計ソフトデータ同期"""
        result = {
            "success": False,
            "sales_synced": 0,
            "expenses_pushed": 0,
            "errors": []
        }
        
        try:
            # 売上データ同期
            sales_results = self.sync_sales_data()
            result["sales_synced"] = len(sales_results)
            
            # 同期時刻更新
            self.config.last_sync = datetime.now()
            result["success"] = True
            
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"会計ソフトデータ同期エラー: {str(e)}")
        
        return result

class IntegrationService:
    """外部システム連携管理サービス"""
    
    def __init__(self):
        self.configs: Dict[str, ExternalSystemConfig] = {}
        self.connectors: Dict[str, ExternalSystemConnector] = {}
    
    def register_system(self, config: ExternalSystemConfig) -> bool:
        """外部システムを登録"""
        try:
            self.configs[config.config_id] = config
            
            # 連携コネクター作成
            if config.system_type == "crm":
                connector = CRMConnector(config)
            elif config.system_type == "accounting":
                connector = AccountingConnector(config)
            else:
                logger.error(f"未対応のシステムタイプ: {config.system_type}")
                return False
            
            self.connectors[config.config_id] = connector
            logger.info(f"外部システム登録完了: {config.system_name}")
            return True
            
        except Exception as e:
            logger.error(f"システム登録エラー: {str(e)}")
            return False
    
    def test_all_connections(self) -> Dict[str, bool]:
        """全システムの接続テスト"""
        results = {}
        
        for config_id, connector in self.connectors.items():
            try:
                results[config_id] = connector.test_connection()
            except Exception as e:
                logger.error(f"接続テストエラー {config_id}: {str(e)}")
                results[config_id] = False
        
        return results
    
    def sync_all_systems(self) -> Dict[str, Dict[str, Any]]:
        """全システムのデータ同期"""
        results = {}
        
        for config_id, connector in self.connectors.items():
            if self.configs[config_id].is_active:
                try:
                    results[config_id] = connector.sync_data()
                except Exception as e:
                    logger.error(f"データ同期エラー {config_id}: {str(e)}")
                    results[config_id] = {
                        "success": False,
                        "errors": [str(e)]
                    }
            else:
                logger.info(f"システム無効のためスキップ: {config_id}")
        
        return results
    
    def sync_specific_system(self, config_id: str) -> Dict[str, Any]:
        """特定システムのデータ同期"""
        if config_id not in self.connectors:
            logger.error(f"未登録システム: {config_id}")
            return {"success": False, "errors": ["システムが見つかりません"]}
        
        if not self.configs[config_id].is_active:
            logger.warning(f"無効化されたシステム: {config_id}")
            return {"success": False, "errors": ["システムが無効化されています"]}
        
        try:
            return self.connectors[config_id].sync_data()
        except Exception as e:
            logger.error(f"データ同期エラー {config_id}: {str(e)}")
            return {"success": False, "errors": [str(e)]}
    
    def push_daily_report_to_crm(self, report_data: Dict) -> bool:
        """日報をCRMにプッシュ"""
        crm_systems = [config_id for config_id, config in self.configs.items() 
                      if config.system_type == "crm" and config.is_active]
        
        if not crm_systems:
            logger.warning("アクティブなCRMシステムがありません")
            return False
        
        success_count = 0
        for config_id in crm_systems:
            try:
                connector = self.connectors[config_id]
                if isinstance(connector, CRMConnector):
                    activity_data = self._convert_report_to_activity(report_data)
                    if connector.push_sales_activity(activity_data):
                        success_count += 1
            except Exception as e:
                logger.error(f"CRMプッシュエラー {config_id}: {str(e)}")
        
        return success_count > 0
    
    def push_expenses_to_accounting(self, expense_data: Dict) -> bool:
        """経費を会計ソフトにプッシュ"""
        accounting_systems = [config_id for config_id, config in self.configs.items() 
                             if config.system_type == "accounting" and config.is_active]
        
        if not accounting_systems:
            logger.warning("アクティブな会計ソフトがありません")
            return False
        
        success_count = 0
        for config_id in accounting_systems:
            try:
                connector = self.connectors[config_id]
                if isinstance(connector, AccountingConnector):
                    if connector.push_expense_data(expense_data):
                        success_count += 1
            except Exception as e:
                logger.error(f"会計ソフトプッシュエラー {config_id}: {str(e)}")
        
        return success_count > 0
    
    def get_system_status(self) -> Dict[str, Dict]:
        """システム状況一覧を取得"""
        status = {}
        
        for config_id, config in self.configs.items():
            status[config_id] = {
                "system_name": config.system_name,
                "system_type": config.system_type,
                "is_active": config.is_active,
                "last_sync": config.last_sync,
                "sync_frequency": config.sync_frequency,
                "connection_status": "unknown"
            }
            
            # 接続状況チェック
            if config_id in self.connectors:
                try:
                    status[config_id]["connection_status"] = "connected" if self.connectors[config_id].test_connection() else "disconnected"
                except:
                    status[config_id]["connection_status"] = "error"
        
        return status
    
    def _convert_report_to_activity(self, report_data: Dict) -> Dict:
        """日報データをCRM活動データに変換"""
        return {
            "activity_id": report_data.get("report_id"),
            "user_id": report_data.get("user_id"),
            "date": report_data.get("report_date"),
            "activity_type": "daily_report",
            "summary": f"営業日報: 訪問{len(report_data.get('visits', []))}件、売上{len(report_data.get('sales_results', []))}件",
            "details": {
                "working_hours": report_data.get("working_hours"),
                "visits": report_data.get("visits", []),
                "sales_results": report_data.get("sales_results", []),
                "challenges": report_data.get("challenges"),
                "next_actions": report_data.get("next_actions")
            }
        }

# テスト用のメイン関数
def main():
    """テスト用メイン関数"""
    logger.info("外部システム連携サービス初期化開始...")
    
    service = IntegrationService()
    
    # サンプル CRMシステム設定
    crm_config = ExternalSystemConfig(
        config_id="crm_001",
        system_name="SampleCRM",
        system_type="crm",
        api_endpoint="https://api.samplecrm.com/v1",
        api_key="sample_crm_api_key",
        sync_frequency="daily"
    )
    
    # サンプル 会計ソフト設定
    accounting_config = ExternalSystemConfig(
        config_id="acc_001",
        system_name="SampleAccounting",
        system_type="accounting",
        api_endpoint="https://api.sampleaccounting.com/v1",
        api_key="sample_accounting_api_key",
        sync_frequency="daily"
    )
    
    # システム登録
    service.register_system(crm_config)
    service.register_system(accounting_config)
    
    # システム状況確認
    status = service.get_system_status()
    logger.info(f"登録システム数: {len(status)}")
    
    # テスト用日報データをCRMにプッシュ
    sample_report = {
        "report_id": "rpt_u001_20240326",
        "user_id": "u001",
        "report_date": "2024-03-26",
        "visits": [{"customer_id": "c001", "purpose": "商品提案"}],
        "sales_results": [{"product_id": "p001", "amount": 59800}],
        "working_hours": 8.0,
        "challenges": "価格競争激化",
        "next_actions": "見積書提出"
    }
    
    # CRMプッシュ（実際のAPI呼び出しはしない、ログのみ）
    logger.info("日報CRMプッシュテスト実行（実際の通信は行いません）")
    
    logger.info("外部システム連携サービステスト完了")

if __name__ == "__main__":
    main()
