import os
import json
import uuid
import re
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from azure.data.tables import TableServiceClient, TableClient, UpdateMode
    from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
    AZURE_TABLES_AVAILABLE = True
except ImportError:
    AZURE_TABLES_AVAILABLE = False


def _safe_serialize_val(val: Any) -> Any:
    """Ensure value can be stored in Azure Table Storage (which allows str, int, float, bool, bytes, datetime)."""
    if isinstance(val, (list, dict)):
        return json.dumps(val, default=str)
    return val


def _safe_deserialize_val(val: Any) -> Any:
    """Deserialize JSON strings if applicable."""
    if isinstance(val, str) and (val.startswith("[") or val.startswith("{")):
        try:
            return json.loads(val)
        except Exception:
            return val
    return val


class AzureTableWrapper:
    """
    Seamless drop-in replacement for boto3 DynamoDB Table using Azure Table Storage.
    Provides get_item, put_item, update_item, query, scan, and table_status.
    Falls back to a local SQLite database if Azure is unreachable.
    """

    def __init__(self, table_name: str, connection_string: Optional[str] = None):
        self.table_name = table_name.lower().replace("_", "")
        self.raw_name = table_name
        self.connection_string = connection_string or os.getenv("AZURE_TABLE_CONNECTION_STRING")
        self.client: Optional[Any] = None
        self.use_azure = False
        
        # Determine primary partition and row key mapping
        if "user" in self.table_name:
            self.default_pk = "users"
            self.rk_field = "phone_number"
        elif "session" in self.table_name:
            self.default_pk = "sessions"
            self.rk_field = "session_id"
        elif "querie" in self.table_name or "query" in self.table_name:
            self.default_pk = "queries"
            self.rk_field = "query_id"
        elif "village" in self.table_name:
            self.default_pk = "villages"
            self.rk_field = "village_id"
        elif "report" in self.table_name:
            self.default_pk = "reports"
            self.rk_field = "report_id"
        elif "crop" in self.table_name:
            self.default_pk = "crops"
            self.rk_field = "crop_id"
        elif "location" in self.table_name:
            self.default_pk = "locations"
            self.rk_field = "location_id"
        elif "advisory" in self.table_name or "news" in self.table_name:
            self.default_pk = "advisories"
            self.rk_field = "advisory_id"
        elif "market" in self.table_name or "price" in self.table_name:
            self.default_pk = "markets"
            self.rk_field = "record_id"
        elif "soil" in self.table_name:
            self.default_pk = "soil"
            self.rk_field = "soil_id"
        else:
            self.default_pk = "general"
            self.rk_field = "id"

        self._init_client()
        self._init_sqlite_fallback()

    def _init_client(self):
        if not AZURE_TABLES_AVAILABLE or not self.connection_string:
            return

        try:
            service = TableServiceClient.from_connection_string(self.connection_string)
            # Ensure table exists
            try:
                service.create_table(self.table_name)
            except Exception:
                pass
            self.client = service.get_table_client(self.table_name)
            self.use_azure = True
            print(f"✅ Connected to Azure Table Storage: {self.table_name}")
        except Exception as e:
            print(f"⚠️ Could not connect to Azure Table Storage for {self.table_name} ({e}). Using local fallback.")
            self.use_azure = False

    def _init_sqlite_fallback(self):
        os.makedirs("data", exist_ok=True)
        self.db_path = os.path.join("data", "sarthi_local.db")
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        pk TEXT,
                        rk TEXT PRIMARY KEY,
                        data TEXT,
                        created_at TEXT
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"SQLite init error: {e}")

    @property
    def table_status(self) -> str:
        return "ACTIVE"

    def _entity_to_dict(self, entity: dict) -> dict:
        item = {}
        for k, v in entity.items():
            if k in ("PartitionKey", "RowKey", "Timestamp", "etag"):
                continue
            item[k] = _safe_deserialize_val(v)
        
        # Ensure key field exists
        if self.rk_field not in item and "RowKey" in entity:
            item[self.rk_field] = entity["RowKey"]
        return item

    def get_item(self, Key: dict) -> dict:
        """DynamoDB compatible get_item."""
        rk_val = Key.get(self.rk_field) or list(Key.values())[0]
        pk_val = Key.get("user_phone") or self.default_pk

        if self.use_azure and self.client:
            try:
                # Query by RowKey across partitions or direct fetch
                try:
                    entity = self.client.get_entity(pk_val, str(rk_val))
                    return {"Item": self._entity_to_dict(dict(entity))}
                except ResourceNotFoundError:
                    # Try default partition
                    if pk_val != self.default_pk:
                        entity = self.client.get_entity(self.default_pk, str(rk_val))
                        return {"Item": self._entity_to_dict(dict(entity))}
                    return {}
                except Exception:
                    # Scan query for RowKey if partition differs
                    query_filter = f"RowKey eq '{rk_val}'"
                    entities = list(self.client.query_entities(query_filter, results_per_page=1))
                    if entities:
                        return {"Item": self._entity_to_dict(dict(entities[0]))}
                    return {}
            except Exception as e:
                print(f"Azure Table get_item error ({self.table_name}): {e}. Trying SQLite fallback.")

        # SQLite fallback
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT data FROM {self.table_name} WHERE rk = ?", (str(rk_val),))
                row = cursor.fetchone()
                if row:
                    return {"Item": json.loads(row[0])}
        except Exception as sqle:
            print(f"SQLite get_item error: {sqle}")
        return {}

    def put_item(self, Item: dict) -> dict:
        """DynamoDB compatible put_item."""
        item = Item.copy()
        rk_val = str(item.get(self.rk_field) or item.get("RowKey") or item.get("id") or uuid.uuid4())
        pk_val = str(item.get("user_phone") or item.get("PartitionKey") or self.default_pk)

        item[self.rk_field] = rk_val

        if self.use_azure and self.client:
            try:
                azure_entity = {
                    "PartitionKey": pk_val,
                    "RowKey": rk_val
                }
                for k, v in item.items():
                    azure_entity[k] = _safe_serialize_val(v)
                self.client.upsert_entity(azure_entity, mode=UpdateMode.REPLACE)
            except Exception as e:
                print(f"Azure Table put_item error ({self.table_name}): {e}. Saving to SQLite fallback.")

        # Always keep SQLite in sync as backup
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    f"INSERT OR REPLACE INTO {self.table_name} (pk, rk, data, created_at) VALUES (?, ?, ?, ?)",
                    (pk_val, rk_val, json.dumps(item, default=str), datetime.utcnow().isoformat())
                )
                conn.commit()
        except Exception as sqle:
            print(f"SQLite put_item error: {sqle}")

        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def update_item(self, Key: dict, UpdateExpression: str = "", ExpressionAttributeValues: dict = None) -> dict:
        """DynamoDB compatible update_item with expression parsing."""
        current = self.get_item(Key).get("Item", {})
        if not current:
            current = Key.copy()

        # Parse SET expressions like "SET location = :loc, helpful = :h"
        if UpdateExpression and ExpressionAttributeValues:
            # Extract assignments: field = :placeholder
            matches = re.findall(r"(\w+)\s*=\s*:(\w+)", UpdateExpression)
            for field, placeholder in matches:
                full_placeholder = f":{placeholder}"
                if full_placeholder in ExpressionAttributeValues:
                    current[field] = ExpressionAttributeValues[full_placeholder]
                elif placeholder in ExpressionAttributeValues:
                    current[field] = ExpressionAttributeValues[placeholder]

        # Also fallback to direct key stripping if no matches were parsed
        if ExpressionAttributeValues and not re.search(r"\w+\s*=\s*:\w+", UpdateExpression):
            for k, v in ExpressionAttributeValues.items():
                field_name = k.lstrip(":")
                current[field_name] = v

        return self.put_item(Item=current)

    def query(self, KeyConditionExpression=None, IndexName=None, ScanIndexForward=True, Limit=100, **kwargs) -> dict:
        """DynamoDB compatible query."""
        items = []
        user_phone = None
        
        # Extract user_phone from KeyConditionExpression if provided
        if KeyConditionExpression is not None:
            expr_str = str(KeyConditionExpression)
            # Try to extract the literal value from expressions like Key('user_phone').eq(...)
            match = re.search(r"['\"]([^'\"]+)['\"]", expr_str)
            if match:
                user_phone = match.group(1)

        if self.use_azure and self.client:
            try:
                if user_phone:
                    filter_str = f"user_phone eq '{user_phone}' or PartitionKey eq '{user_phone}'"
                    entities = self.client.query_entities(filter_str, results_per_page=Limit)
                else:
                    entities = self.client.list_entities(results_per_page=Limit)

                for e in entities:
                    items.append(self._entity_to_dict(dict(e)))
                
                # Sort by timestamp descending if needed
                items.sort(key=lambda x: x.get("timestamp", x.get("created_at", "")), reverse=not ScanIndexForward)
                return {"Items": items[:Limit]}
            except Exception as e:
                print(f"Azure Table query error ({self.table_name}): {e}. Falling back to SQLite.")

        # SQLite fallback
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if user_phone:
                    cursor.execute(f"SELECT data FROM {self.table_name} WHERE pk = ? OR data LIKE ?", 
                                   (user_phone, f'%"{user_phone}"%'))
                else:
                    cursor.execute(f"SELECT data FROM {self.table_name}")
                rows = cursor.fetchall()
                for r in rows:
                    items.append(json.loads(r[0]))
                items.sort(key=lambda x: x.get("timestamp", x.get("created_at", "")), reverse=not ScanIndexForward)
                return {"Items": items[:Limit]}
        except Exception as sqle:
            print(f"SQLite query error: {sqle}")
            return {"Items": []}

    def scan(self, Limit=100, **kwargs) -> dict:
        """DynamoDB compatible scan."""
        items = []
        if self.use_azure and self.client:
            try:
                entities = self.client.list_entities(results_per_page=Limit)
                for e in entities:
                    items.append(self._entity_to_dict(dict(e)))
                return {"Items": items[:Limit]}
            except Exception as e:
                print(f"Azure Table scan error ({self.table_name}): {e}. Falling back to SQLite.")

        # SQLite fallback
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT data FROM {self.table_name} LIMIT ?", (Limit,))
                rows = cursor.fetchall()
                for r in rows:
                    items.append(json.loads(r[0]))
                return {"Items": items}
        except Exception as sqle:
            print(f"SQLite scan error: {sqle}")
            return {"Items": []}


class AzureTableDatabase:
    """Manager to return AzureTableWrapper instances for each table."""

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv("AZURE_TABLE_CONNECTION_STRING")

    def Table(self, table_name: str) -> AzureTableWrapper:
        return AzureTableWrapper(table_name, self.connection_string)


def get_azure_table_db() -> AzureTableDatabase:
    return AzureTableDatabase()
