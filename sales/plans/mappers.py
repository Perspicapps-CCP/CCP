from rpc_clients.suppliers_client import SuppliersClient
from rpc_clients.users_client import UsersClient

from .models import SalesPlan
from .schemas import SalesPlanDetailSchema


def plan_to_schema(sales_plan: SalesPlan) -> SalesPlanDetailSchema:
    """
    Convert a SalesPlan object to a SalesPlanDetailSchema object.
    """
    sellers = UsersClient().get_sellers(
        [seller.seller_id for seller in sales_plan.sellers]
    )
    product = SuppliersClient().get_product(sales_plan.product_id)

    return SalesPlanDetailSchema(
        id=sales_plan.id,
        product=product,
        goal=sales_plan.goal,
        start_date=sales_plan.start_date,
        end_date=sales_plan.end_date,
        sellers=sellers,
        created_at=sales_plan.created_at,
        updated_at=sales_plan.updated_at,
    )
