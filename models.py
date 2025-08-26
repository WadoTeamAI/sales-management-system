#!/usr/bin/env python3
"""
空気清浄機販売営業向け日報・目標管理システム - データモデル
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from enum import Enum
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """ユーザー権限"""
    SALES = "sales"           # 営業担当者
    TEAM_LEADER = "team_leader"  # チームリーダー
    MANAGER = "manager"       # 部長/マネージャー
    ADMIN = "admin"          # システム管理者

class ProductCategory(Enum):
    """商品カテゴリ"""
    HOME_USE = "home_use"     # 家庭用
    BUSINESS_USE = "business_use"  # 業務用
    INDUSTRIAL_USE = "industrial_use"  # 工業用

class TargetType(Enum):
    """目標タイプ"""
    SALES_AMOUNT = "sales_amount"    # 売上目標
    PROFIT = "profit"               # 利益目標
    QUANTITY = "quantity"           # 販売数量
    NEW_CUSTOMER = "new_customer"   # 新規顧客獲得

class AlertLevel(Enum):
    """アラートレベル"""
    INFO = "info"
    WARNING = "warning" 
    CRITICAL = "critical"

@dataclass
class User:
    """ユーザー情報"""
    user_id: str
    name: str
    email: str
    role: UserRole
    team_id: Optional[str] = None
    manager_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class Team:
    """チーム情報"""
    team_id: str
    team_name: str
    manager_id: str
    member_ids: List[str] = field(default_factory=list)
    target_area: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Product:
    """商品情報"""
    product_id: str
    product_name: str
    model_number: str
    category: ProductCategory
    price: int
    cost: int
    specifications: Dict[str, str] = field(default_factory=dict)
    stock_quantity: int = 0
    is_active: bool = True
    launch_date: Optional[date] = None

@dataclass
class Customer:
    """顧客情報"""
    customer_id: str
    company_name: str
    contact_person: str
    email: str
    phone: str
    address: str
    industry: str
    customer_type: str  # 新規/既存
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class DailyReport:
    """日報"""
    report_id: str
    user_id: str
    report_date: date
    activities: List[Dict[str, str]] = field(default_factory=list)
    visits: List[Dict[str, str]] = field(default_factory=list)
    sales_results: List[Dict[str, str]] = field(default_factory=list)
    challenges: str = ""
    next_actions: str = ""
    working_hours: float = 8.0
    travel_expense: int = 0
    status: str = "draft"  # draft, submitted, approved
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None

@dataclass
class Target:
    """目標"""
    target_id: str
    user_id: str
    target_type: TargetType
    period_start: date
    period_end: date
    target_value: float
    current_value: float = 0.0
    product_id: Optional[str] = None  # 商品別目標の場合
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class SalesResult:
    """販売実績"""
    result_id: str
    user_id: str
    customer_id: str
    product_id: str
    quantity: int
    unit_price: int
    total_amount: int
    profit_amount: int
    sale_date: date
    contract_date: Optional[date] = None
    delivery_date: Optional[date] = None
    status: str = "contracted"  # quoted, contracted, delivered, completed

@dataclass
class Visit:
    """訪問記録"""
    visit_id: str
    user_id: str
    customer_id: str
    visit_date: datetime
    purpose: str
    participants: List[str] = field(default_factory=list)
    discussion_points: str = ""
    outcome: str = ""
    next_action: str = ""
    products_discussed: List[str] = field(default_factory=list)
    follow_up_date: Optional[date] = None

@dataclass
class Alert:
    """アラート"""
    alert_id: str
    user_id: str
    alert_type: str
    level: AlertLevel
    title: str
    message: str
    target_id: Optional[str] = None
    is_read: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

@dataclass
class AnalyticsResult:
    """分析結果"""
    analysis_id: str
    user_id: str
    analysis_type: str
    period_start: date
    period_end: date
    metrics: Dict[str, float] = field(default_factory=dict)
    charts_data: Dict[str, List] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ExternalSystemConfig:
    """外部システム連携設定"""
    config_id: str
    system_name: str
    system_type: str  # crm, accounting
    api_endpoint: str
    api_key: str
    sync_frequency: str  # daily, weekly, monthly
    last_sync: Optional[datetime] = None
    is_active: bool = True

# サンプルデータ生成関数
def create_sample_data():
    """開発用サンプルデータを生成"""
    
    # サンプルユーザー
    users = [
        User("u001", "田中太郎", "tanaka@company.com", UserRole.SALES, "t001"),
        User("u002", "佐藤花子", "sato@company.com", UserRole.SALES, "t001"),
        User("u003", "山田次郎", "yamada@company.com", UserRole.TEAM_LEADER, "t001"),
        User("u004", "鈴木一郎", "suzuki@company.com", UserRole.MANAGER)
    ]
    
    # サンプルチーム
    teams = [
        Team("t001", "東京営業チーム", "u003", ["u001", "u002"], "東京・神奈川エリア")
    ]
    
    # サンプル商品
    products = [
        Product("p001", "エアクリーン Pro", "AC-P001", ProductCategory.HOME_USE, 
               59800, 35000, {"適用面積": "25畳", "フィルター": "HEPA", "消費電力": "45W"}),
        Product("p002", "エアクリーン Business", "AC-B001", ProductCategory.BUSINESS_USE,
               198000, 120000, {"適用面積": "100㎡", "フィルター": "ULPA", "消費電力": "180W"})
    ]
    
    return {
        "users": users,
        "teams": teams, 
        "products": products
    }

if __name__ == "__main__":
    logger.info("データモデルの初期化完了")
    sample_data = create_sample_data()
    logger.info(f"サンプルデータ生成: ユーザー{len(sample_data['users'])}名、商品{len(sample_data['products'])}点")
