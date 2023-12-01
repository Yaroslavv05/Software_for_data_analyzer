import logging

from celery import shared_task

from main.services.data_fetching import DataFetchingService
from main.services.data_processing import ProcessData

fetching_service = DataFetchingService()
processing_service = ProcessData()


logger = logging.getLogger(__name__)


@shared_task
def fetch_and_process_data_task(
    symbol, exchange, open_price, bound_up, bound_low, date, time_frame
):
    """
    Process data task
    """
    try:
        data = fetching_service.get_minute_interval(
            symbol, exchange, open_price, bound_up, bound_low, date, time_frame
        )
        if data:
            processing_service.calculate_some_data(data)
            processing_service.generate_excel(data)
            logger.info(f"Data processing completed successfully")
    except Exception as e:
        logger.info(f"An error occurred while processing data: {e}")
