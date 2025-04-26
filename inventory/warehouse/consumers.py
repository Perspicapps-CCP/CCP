from typing import Dict, List
from database import SessionLocal

from rpc_clients.schemas import GetWarehousesResponseSchema
from seedwork.base_consumer import BaseConsumer
from warehouse import mappers
from .services import get_warehouses


class GetWarehousesConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(queue="inventory.get_warehouses")

    def process_payload(self, payload: Dict) -> List[Dict]:
        db = SessionLocal()
        try:
            warehouses_list = get_warehouses(db)
            return GetWarehousesResponseSchema(
                warehouses=mappers.warehouse_list_to_schema(warehouses_list)
            ).model_dump_json()
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()
