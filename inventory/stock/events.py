from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from stock import services
from stock.mappers import aggr_stock_event_to_schema
from stock.models import Stock
from stock.publishers import publish_stock_change


def setup_db_events():

    @event.listens_for(Stock, 'after_update')
    def receive_after_update(mapper, connection, target: Stock):
        Session = sessionmaker(bind=connection)
        session = Session(bind=connection)
        product = services.get_product_aggregated(session, target.product_id)
        event = aggr_stock_event_to_schema("update_stock", product)
        publish_stock_change(event)
        session.close()
