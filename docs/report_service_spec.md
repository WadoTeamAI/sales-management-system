# `report_service.py` 技術仕様書

## 1. 概要

このドキュメントは、営業管理アプリケーションにおける営業日報の管理を担当するサービス `report_service.py` の技術的な仕様を定義します。

`ReportService` クラスは、日報のライフサイクル（作成、更新、提出、承認）、関連データ（訪問記録、販売実績）の追加、および統計情報の集計とエクスポート機能を提供します。

## 2. 主な機能

-   日報のCRUD（作成、読み取り、更新、削除）操作
-   日報のステータス管理（下書き, 提出済み, 承認済み）
-   ユーザー、期間に基づく日報の検索
-   承認者向けの承認待ち日報一覧の提供
-   日報に関連する訪問記録および販売実績の追加
-   指定期間におけるユーザーの活動統計の集計
-   日報未提出者に対するアラート生成
-   日報データのエクスポート（CSV形式）

## 3. クラスとメソッドの詳細

### `ReportService`

営業日報管理サービスのメインクラス。

---

#### `create_daily_report(user_id: str, report_date: date) -> DailyReport`

-   **説明**: 新しい日報を作成します。指定されたユーザーIDと日付で既に日報が存在する場合は、既存の日報を返します。
-   **引数**:
    -   `user_id (str)`: 日報を作成するユーザーのID。
    -   `report_date (date)`: 日報の日付。
-   **戻り値**: `DailyReport` オブジェクト。

---

#### `update_daily_report(report_id: str, updates: Dict) -> bool`

-   **説明**: 既存の日報を更新します。承認済みの日報は編集できません。
-   **引数**:
    -   `report_id (str)`: 更新対象の日報ID。
    -   `updates (Dict)`: 更新内容を含む辞書。
-   **戻り値**: 更新が成功した場合は `True`、失敗した場合は `False`。

---

#### `submit_daily_report(report_id: str) -> bool`

-   **説明**: 日報を提出済みのステータスに変更します。提出前にバリデーションが実行されます。
-   **引数**:
    -   `report_id (str)`: 提出する日報ID。
-   **戻り値**: 提出が成功した場合は `True`、失敗した場合は `False`。

---

#### `approve_daily_report(report_id: str, approver_id: str) -> bool`

-   **説明**: 提出された日報を承認済みのステータスに変更します。
-   **引数**:
    -   `report_id (str)`: 承認する日報ID。
    -   `approver_id (str)`: 承認者のユーザーID。
-   **戻り値**: 承認が成功した場合は `True`、失敗した場合は `False`。

---

#### `get_user_reports(user_id: str, start_date: date, end_date: date) -> List[DailyReport]`

-   **説明**: 指定されたユーザーと期間の日報一覧を取得します。
-   **引数**:
    -   `user_id (str)`: 検索対象のユーザーID。
    -   `start_date (date)`: 検索期間の開始日。
    -   `end_date (date)`: 検索期間の終了日。
-   **戻り値**: `DailyReport` オブジェクトのリスト。

---

#### `get_pending_approvals(approver_id: str) -> List[DailyReport]`

-   **説明**: 指定された承認者が承認すべき、提出済みの日報一覧を取得します。
-   **引数**:
    -   `approver_id (str)`: 承認者のユーザーID。
-   **戻り値**: `DailyReport` オブジェクトのリスト。

---

#### `get_report_statistics(user_id: str, period_days: int = 30) -> Dict`

-   **説明**: 指定されたユーザーの過去N日間の活動統計（日報提出率、訪問件数など）を取得します。
-   **引数**:
    -   `user_id (str)`: 統計を取得するユーザーID。
    -   `period_days (int)`: 集計期間（日数）。デフォルトは30日。
-   **戻り値**: 統計情報を含む辞書。

---

#### `export_reports_to_csv(user_id: str, start_date: date, end_date: date) -> str`

-   **説明**: 指定されたユーザーと期間の日報データをCSV形式の文字列としてエクスポートします。
-   **引数**:
    -   `user_id (str)`: 対象ユーザーのID。
    -   `start_date (date)`: 期間の開始日。
    -   `end_date (date)`: 期間の終了日。
-   **戻り値**: CSV形式の文字列。
