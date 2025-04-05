import uuid

import faker

from plans import mappers
from plans.models import SalesPlan, SellerInPlan
from plans.schemas import SalesPlanDetailSchema

fake = faker.Faker()


def test_plan_to_schema():
    """
    Test the plan_to_schema function.
    """
    # Create a mock SalesPlan object
    plan_id = uuid.UUID(fake.uuid4())
    sales_plan = SalesPlan(
        id=plan_id,
        product_id=uuid.UUID(fake.uuid4()),
        goal=fake.random_int(min=1, max=1000),
        start_date=fake.date_time().date(),
        end_date=fake.date_time().date(),
        sellers=[
            SellerInPlan(
                plan_id=plan_id,
                id=uuid.UUID(fake.uuid4()),
                seller_id=uuid.UUID(fake.uuid4()),
                created_at=fake.date_time(),
                updated_at=fake.date_time(),
            )
            for _ in range(2)
        ],
        created_at=fake.date_time(),
        updated_at=fake.date_time(),
    )

    # Call the function to test
    result = mappers.plan_to_schema(sales_plan)

    # Assert the result is of type SalesPlanDetailSchema
    assert isinstance(result, SalesPlanDetailSchema)

    assert result.id == sales_plan.id
    assert result.product.id == sales_plan.product_id
    assert result.goal == sales_plan.goal
    assert result.start_date == sales_plan.start_date
    assert result.end_date == sales_plan.end_date
    assert result.created_at == sales_plan.created_at
    assert result.updated_at == sales_plan.updated_at
    assert len(result.sellers) == len(sales_plan.sellers)
    for i, seller in enumerate(result.sellers):
        assert seller.id == sales_plan.sellers[i].seller_id
