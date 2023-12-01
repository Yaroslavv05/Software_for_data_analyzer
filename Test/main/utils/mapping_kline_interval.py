from enum import Enum


class KlineInterval(Enum):
    ONE_MINUTE = 0.0166666667
    THREE_MINUTES = 0.05
    FIVE_MINUTES = 0.0833333333
    FIFTEEN_MINUTES = 0.25
    THIRTY_MINUTES = 0.5
    ONE_HOUR = 1.0
    TWO_HOURS = 2.0
    FOUR_HOURS = 4.0
    SIX_HOURS = 6.0
    EIGHT_HOURS = 8.0
    TWELVE_HOURS = 12.0
    ONE_DAY = 24.0
    THREE_DAYS = 72.0
    ONE_WEEK = 168.0
    ONE_MONTH = 720.0


def generate_interval_mapping():
    return {
        KlineInterval.ONE_MINUTE: Client.KLINE_INTERVAL_1MINUTE,
        KlineInterval.THREE_MINUTES: Client.KLINE_INTERVAL_3MINUTE,
        KlineInterval.FIVE_MINUTES: Client.KLINE_INTERVAL_5MINUTE,
        KlineInterval.FIFTEEN_MINUTES: Client.KLINE_INTERVAL_15MINUTE,
        KlineInterval.THIRTY_MINUTES: Client.KLINE_INTERVAL_30MINUTE,
        KlineInterval.ONE_HOUR: Client.KLINE_INTERVAL_1HOUR,
        KlineInterval.TWO_HOURS: Client.KLINE_INTERVAL_2HOUR,
        KlineInterval.FOUR_HOURS: Client.KLINE_INTERVAL_4HOUR,
        KlineInterval.SIX_HOURS: Client.KLINE_INTERVAL_6HOUR,
        KlineInterval.EIGHT_HOURS: Client.KLINE_INTERVAL_8HOUR,
        KlineInterval.TWELVE_HOURS: Client.KLINE_INTERVAL_12HOUR,
        KlineInterval.ONE_DAY: Client.KLINE_INTERVAL_1DAY,
        KlineInterval.THREE_DAYS: Client.KLINE_INTERVAL_3DAY,
        KlineInterval.ONE_WEEK: Client.KLINE_INTERVAL_1WEEK,
        KlineInterval.ONE_MONTH: Client.KLINE_INTERVAL_1MONTH,
    }
