import pandas as pd  # type: ignore
from aat.config import Side
from aat.core import Event, Order, Trade, Instrument, ExchangeType, Position
from aat.core.engine.manager import ManagerBase

from .portfolio import Portfolio


class PortfolioManager(ManagerBase):
    def __init__(self):
        self._portfolio = Portfolio()

        # Track prices over time
        self._prices = {}
        self._trades = {}

        # Track active (open) orders
        self._active_orders = []

        # Track active positions
        self._active_positions = {}

    def _setManager(self, manager):
        '''install manager'''
        self._manager = manager

    def newPosition(self, strategy, trade: Trade):
        self._portfolio.newPosition(strategy, trade)

    # *********************
    # Risk Methods        *
    # *********************
    def positions(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        return self._portfolio.positions(instrument=instruent, exchange=exchange, side=side)

    def priceHistory(self, instrument: Instrument = None):
        if instrument:
            return pd.DataFrame(self._prices[instrument], columns=[instrument.name, 'when'])
        return {i: pd.DataFrame(self._prices[i], columns=[i.name, 'when']) for i in self._prices}

    # **********************
    # EventHandler methods *
    # **********************
    async def onTrade(self, event: Event):
        trade: Trade = event.target  # type: ignore
        self._portfolio.onTrade(trade)

    async def onCancel(self, event):
        # TODO
        pass

    async def onOpen(self, event: Event):
        # TODO
        pass

    async def onFill(self, event: Event):
        # TODO
        pass

    async def onChange(self, event: Event):
        # TODO
        pass

    async def onData(self, event: Event):
        # TODO
        pass

    async def onHalt(self, event: Event):
        # TODO
        pass

    async def onContinue(self, event: Event):
        # TODO
        pass

    async def onError(self, event: Event):
        # TODO
        pass

    async def onStart(self, event: Event):
        # TODO
        pass

    async def onExit(self, event: Event):
        # TODO
        pass

    #########################
    # Order Entry Callbacks #
    #########################
    async def onTraded(self, event: Event):
        trade: Trade = event.target  # type: ignore
        self._portfolio.onTraded(trade)
