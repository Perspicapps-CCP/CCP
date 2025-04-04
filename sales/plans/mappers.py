from typing import Dict

from rpc_clients.suppliers_client import SuppliersClient
from rpc_clients.users_client import UsersClient

from .models import SalesPlan
from .schemas import SalesPlanDetailSchema


def _plan_to_schema(
    sales_plan: SalesPlan, sellers: Dict, products: Dict
) -> SalesPlanDetailSchema:
    """
    Convert a SalesPlan object to a SalesPlanDetailSchema object.
    """
    return SalesPlanDetailSchema(
        id=sales_plan.id,
        product=products[sales_plan.product_id],
        goal=sales_plan.goal,
        start_date=sales_plan.start_date,
        end_date=sales_plan.end_date,
        sellers=[sellers[seller.seller_id] for seller in sales_plan.sellers],
        created_at=sales_plan.created_at,
        updated_at=sales_plan.updated_at,
    )


def plan_to_schema(sales_plan: SalesPlan) -> SalesPlanDetailSchema:
    """
    Convert a SalesPlan object to a SalesPlanDetailSchema object.
    """
    sellers = UsersClient().get_sellers(
        [seller.seller_id for seller in sales_plan.sellers]
    )
    product = SuppliersClient().get_product(sales_plan.product_id)

    return _plan_to_schema(
        sales_plan=sales_plan,
        sellers={s.id: s for s in sellers},
        products={product.id: product},
    )


def plans_to_schema(plans: list[SalesPlan]) -> list[SalesPlanDetailSchema]:
    """
    Convert a list of SalesPlan objects to a list
      of SalesPlanDetailSchema objects.
    """
    # Get all seller IDs from the plans
    seller_ids = {
        seller.seller_id for plan in plans for seller in plan.sellers
    }
    # Get all product IDs from the plans
    product_ids = {plan.product_id for plan in plans}
    # Fetch sellers and products in bulk
    sellers = {u.id: u for u in UsersClient().get_sellers(seller_ids)}
    products = {p.id: p for p in SuppliersClient().get_products(product_ids)}
    result = []
    for plan in plans:
        result.append(
            _plan_to_schema(
                sales_plan=plan,
                sellers=sellers,
                products=products,
            )
        )
    return result
