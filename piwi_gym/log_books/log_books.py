import logging
import time as t


class TradeHistoryLogBook(object):
    def __init__(self, filename='trade_logbook_{}.log'):
        super().__init__()
        self._filename = filename.format(t.strftime('%Y_%M_%d'))
        self._base_config = logging.basicConfig(filename=self._filename,
                                                format='%(message)s', filemode='w',
                                                level=logging.INFO)
        self._logbook = logging.getLogger('TradeHistoryLogBook')

    def record_info(self, info):
        self._logbook.info(info)

    def record_error(self, error):
        self._logbook.error(error)

    def record_exception(self, exception):
        self._logbook.exception(exception)

