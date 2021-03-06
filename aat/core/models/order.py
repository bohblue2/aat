from datetime import datetime
from typing import Mapping, Union, Type

from ..exchange import ExchangeType
from ..instrument import Instrument
from ...common import _in_cpp
from ...config import DataType, OrderFlag, OrderType, Side


try:
    from aat.binding import OrderCpp  # type: ignore
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_order(volume, price, side, instrument, exchange=ExchangeType(""), notional=0.0, order_type=OrderType.MARKET, flag=OrderFlag.NONE, stop_target=None):
    '''helper method to ensure all arguments are setup'''
    return OrderCpp(0, datetime.now(), volume, price, side, instrument, exchange, notional, order_type, flag, stop_target)


class Order(object):
    __slots__ = [
        "__id",
        "__timestamp",
        "__type",
        "__instrument",
        "__exchange",
        "__volume",
        "__price",
        "__notional",
        "__filled",
        "__side",
        "__order_type",
        "__flag",
        "__stop_target",
    ]

    # for convenience
    Types = OrderType
    Sides = Side
    Flags = OrderFlag

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_order(*args, **kwargs)
        return super(Order, cls).__new__(cls)

    def __init__(self, volume, price, side, instrument, exchange=ExchangeType(""), notional=0.0, order_type=OrderType.MARKET, flag=OrderFlag.NONE, stop_target=None):
        self.__id = 0  # on construction, provide no ID until exchange assigns one
        self.__timestamp = datetime.now()
        self.__type = DataType.ORDER

        assert isinstance(instrument, Instrument)
        assert isinstance(exchange, ExchangeType)
        self.__instrument = instrument
        self.__exchange = exchange

        assert isinstance(volume, (int, float))
        assert volume < float('inf') and ((volume > 0 and order_type != OrderType.STOP) or (order_type == OrderType.STOP and volume == 0))
        assert order_type == OrderType.STOP or ((volume > 0.0) and (volume < float('inf')))
        assert isinstance(price, (int, float))
        assert price < float('inf')
        assert isinstance(side, Side)
        assert isinstance(notional, (int, float))
        assert isinstance(order_type, OrderType)
        assert isinstance(flag, OrderFlag)
        assert (order_type != OrderType.STOP and stop_target is None) or (isinstance(stop_target, Order) and order_type == OrderType.STOP and stop_target.order_type != OrderType.STOP)
        assert order_type != OrderType.STOP or (isinstance(stop_target.instrument, Instrument))

        self.__volume = volume
        self.__price = price
        self.__side = side
        self.__notional = notional
        self.__order_type = order_type
        self.__flag = flag
        self.__stop_target = stop_target

        self.__filled = 0.0

    # TODO
    # @validator("notional")
    # def _assert_notional_set_correct(cls, v, values, **kwargs) -> float:
    #     if values['order_type'] == OrderType.MARKET:
    #         return v
    #     return values['price'] * values['volume']

    # ******** #
    # Readonly #
    # ******** #
    @property
    def type(self) -> OrderType:
        return self.__type

    @property
    def instrument(self) -> Instrument:
        return self.__instrument

    @property
    def exchange(self) -> ExchangeType:
        return self.__exchange

    @property
    def price(self) -> float:
        return self.__price

    @property
    def side(self) -> Side:
        return self.__side

    @property
    def notional(self) -> float:
        return self.__notional

    @property
    def order_type(self) -> OrderType:
        return self.__order_type

    @property
    def flag(self) -> OrderFlag:
        return self.__flag

    @property
    def stop_target(self) -> Union['Order', None]:
        return self.__stop_target

    # ***********#
    # Read/write #
    # ***********#
    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, id: int) -> None:
        assert isinstance(id, int)
        self.__id = id

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    @timestamp.setter
    def timestamp(self, timestamp: datetime) -> None:
        assert isinstance(timestamp, datetime)
        self.__timestamp = timestamp

    @property
    def volume(self) -> float:
        return self.__volume

    @volume.setter
    def volume(self, volume: float) -> None:
        assert isinstance(volume, (int, float))
        assert volume < float('inf') and (volume > 0 or self.order_type == OrderType.STOP)
        assert volume >= self.filled
        self.__volume = volume

    @property
    def filled(self) -> float:
        return self.__filled

    @filled.setter
    def filled(self, filled: float) -> None:
        assert isinstance(filled, (int, float))
        assert filled <= self.volume
        self.__filled = filled

    def __repr__(self) -> str:
        return f'Order( instrument={self.instrument}, timestamp={self.timestamp}, {self.volume}@{self.price}, side={self.side}, exchange={self.exchange})'

    def __eq__(self, other) -> bool:
        assert isinstance(other, Order)
        return self.id == other.id and \
            self.instrument == other.instrument and \
            self.exchange == other.exchange and \
            self.price == other.price and \
            self.volume == other.volume and \
            self.notional == other.notional and \
            self.filled == other.filled

    def toJson(self) -> Mapping[str, Union[str, int, float]]:
        return \
            {'id': self.id,
             'timestamp': self.timestamp.timestamp(),
             'volume': self.volume,
             'price': self.price,
             'side': self.side.value,
             'instrument': self.instrument.toJson(),
             'exchange': self.exchange.toJson(),
             'notional': self.notional,
             'filled': self.filled,
             'order_type': self.order_type.value,
             'flag': self.flag.value,
             'stop_target': self.stop_target.toJson() if self.stop_target else ''  # type: ignore
             }

    @staticmethod
    def fromJson(jsn):
        kwargs = {}
        kwargs['volume'] = jsn['volume']
        kwargs['price'] = jsn['price']
        kwargs['side'] = Side(jsn['side'])
        kwargs['instrument'] = Instrument.fromJson(jsn['instrument'])
        kwargs['exchange'] = ExchangeType.fromJson(jsn['exchange'])

        if 'notional' in jsn and jsn['notional']:
            kwargs['notional'] = jsn['notional']

        if 'flag' in jsn and jsn['flag']:
            kwargs['flag'] = OrderFlag(jsn['flag'])

        if 'stop_target' in jsn and jsn['stop_target']:
            kwargs['stop_target'] = Order.fromJson(jsn['stop_target'])

        if 'order_type' in jsn and jsn['order_type']:
            kwargs['order_type'] = OrderType(jsn['order_type'])

        ret = Order(**kwargs)

        if 'notional' in jsn and jsn['notional']:
            ret.notional = jsn['notional']

        if 'filled' in jsn and jsn['filled']:
            ret.filled = jsn['filled']

        return ret

    @staticmethod
    def perspectiveSchema() -> Mapping[str, Type]:
        return {
            "id": int,
            "timestamp": int,
            "volume": float,
            "price": float,
            "side": str,
            "instrument": str,
            "exchange": str,
        }
