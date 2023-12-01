import logging

logger = logging.getLogger(__name__)


class ProcessData:
    """
    Data processing service, that process candles by chosen algo.
    """

    def __init__(self) -> None:
        pass

    def calculate_some_data(self, data):
        """
        Processing data like calculation and other stuff, related only for pocessing data
        """
        try:
            pass
        except Exception as e:
            logging.info(f"An error occurred while processing data: {e}")

    def generate_excel(self, data):
        """
        Generate excel file with data
        """
        try:
            pass
        except Exception as e:
            logging.info(f"An error occurred while generating excel: {e}")
