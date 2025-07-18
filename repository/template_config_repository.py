from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import json
from typing import Optional, List
from models.order.down_form_order import BaseDownFormOrder

class TemplateConfigRepository:
    DEFAULT_TEMPLATE_META_QUERY = """
        SELECT id, template_code, template_name, is_aggregated, group_by_fields
        FROM export_templates
        WHERE template_code = :template_code
    """
    COLUMN_MAPPINGS_QUERY = """
        SELECT column_order, target_column, source_field, field_type, aggregation_type, transform_config
        FROM template_column_mappings
        WHERE template_id = :template_id AND is_active = TRUE
        ORDER BY column_order
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_template_meta(self, template_code: str) -> Optional[dict]:
        result = await self.session.execute(
            text(self.DEFAULT_TEMPLATE_META_QUERY),
            {"template_code": template_code}
        )
        row = result.first()
        if not row:
            return None
        return {
            "id": row[0],
            "template_code": row[1],
            "template_name": row[2],
            "is_aggregated": row[3],
            "group_by_fields": row[4] or []
        }

    async def _get_column_mappings(self, template_id: int) -> List[dict]:
        result = await self.session.execute(
            text(self.COLUMN_MAPPINGS_QUERY),
            {"template_id": template_id}
        )
        return [
            {
                "column_order": row[0],
                "target_column": row[1],
                "source_field": row[2],
                "field_type": row[3],
                "aggregation_type": row[4],
                "transform_config": json.loads(row[5]) if isinstance(row[5], str) else row[5] or {}
            }
            for row in result.fetchall()
        ]

    def _merge_columns(self, default_columns: List[dict], input_columns: List[dict]) -> List[dict]:
        columns_by_target = {col["target_column"]: col for col in default_columns}
        for col in input_columns:
            columns_by_target[col["target_column"]] = col
        return list(sorted(columns_by_target.values(), key=lambda x: x["column_order"]))

    def _merge_meta(self, default_meta: dict, input_meta: dict) -> dict:
        merged = {**default_meta, **input_meta}
        return merged

    async def get_template_config(self, template_code: str) -> Optional[dict]:
        # 1. Get 'default' template meta and columns
        default_meta = await self._get_template_meta("default")
        if not default_meta:
            return None
        default_id = default_meta["id"]
        default_columns = await self._get_column_mappings(default_id)
        # 2. Get input template meta and columns
        input_meta = await self._get_template_meta(template_code)
        if not input_meta:
            merged_meta = default_meta
            merged_columns = default_columns
        else:
            input_id = input_meta["id"]
            input_columns = await self._get_column_mappings(input_id)
            merged_columns = self._merge_columns(default_columns, input_columns)
            merged_meta = self._merge_meta(default_meta, input_meta)
        return {
            **{k: v for k, v in merged_meta.items() if k != "id"},
            "column_mappings": merged_columns
        }

    async def get_down_form_orders(self, template_code: Optional[str], limit: int = 100, offset: int = 0) -> List[dict]:
        query = select(BaseDownFormOrder)
        if template_code:
            query = query.where(BaseDownFormOrder.form_name == template_code)
        query = query.order_by(BaseDownFormOrder.id.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return [row.__dict__ for row in rows] 