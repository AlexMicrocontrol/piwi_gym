import asyncio
import time
from piwi_gym.configs import *
import json
import os


class MonitoredAccount(object):
    '''Fake Monitored Account. Here are the fictitious purchases and sales made'''

    def __init__(self, start_cash=2.0, start_cryptos=10,
                 buy_limit=0.1, sell_limit=0.9, safe_thresh=0.5,
                 trading_fee=0.2):
        self._start_cash = start_cash
        self._start_cryptos = start_cryptos
        self._buy_limit_pct = buy_limit
        self._sell_limit_pct = sell_limit
        self._safe_thresh = safe_thresh
        self._deposit_thresh = 0.0
        self._wallet = {}
        self._trading_fee = trading_fee
        self.curr_trade = {}
        self.bookkeeping = []

    def reset(self):
        self._wallet = dict(cash=self._start_cash, coins=self._start_cryptos, loss=0.0, profit=0.0)
        self.curr_trade = dict(time_stamp=time.strftime('%m-%d-%Y %H:%M:%S'), trade_type=hLD, quantity=0,
                               total=0., fee=0., ask_price=0.00001, bid_price=0.00001, curr_idx=0,
                               wallet=self._wallet)
        self.bookkeeping.clear()
        self.bookkeeping.append(self.curr_trade)

    def perform_trade_action(self, action, curr_bid_price, curr_ask_price, curr_idx):
        done = False
        if action == BUY:
            done = self.buy_ask(curr_ask_price)
        elif action == SELL:
            done = self.sell_bid(curr_bid_price)
        elif action == HOLD:
            self.curr_trade = {'time_stamp': time.strftime('%m-%d-%Y %H:%M:%S'), 'trade_type': hLD,
                               'quantity': 0, 'total': 0., 'fee': 0.}
        self.curr_trade[ASK] = curr_ask_price
        self.curr_trade[BID] = curr_bid_price
        self.curr_trade[CIDX] = curr_idx
        self.curr_trade['wallet'] = self._wallet
        self.bookkeeping.append(self.curr_trade)

        return done

    def buy_ask(self, ask_price):
        '''Purchases at ask price'''
        cash_expense = self._wallet[CSH] * self._buy_limit_pct
        fee_loss = cash_expense * self._trading_fee
        total_loss = cash_expense + fee_loss
        coins_bought = cash_expense / ask_price
        self._wallet[ASST] += coins_bought
        self._wallet[CSH] -= total_loss
        self._wallet[LSS] += total_loss
        self.curr_trade = {'time_stamp': time.strftime('%m-%d-%Y %H:%M:%S'), 'trade_type': BASK,
                           # 'bid_price': bid_price, 'ask_price': ask_price,
                           'quantity': coins_bought, 'total': total_loss,
                           'fee': fee_loss}
        done = False
        if self._wallet[CSH] < 0.0001:
            done = True

        return done

    def sell_bid(self, bid_price):
        '''sales at bid price'''
        selling_coins = self._wallet[ASST] * self._sell_limit_pct
        cash_takings = selling_coins * bid_price
        fee_loss = cash_takings * self._trading_fee
        total_takings = cash_takings - fee_loss
        self._wallet[ASST] -= selling_coins
        self._wallet[CSH] += total_takings
        self._wallet[PFT] += total_takings
        self.curr_trade = {'time_stamp': time.strftime('%m-%d-%Y %H:%M:%S'), 'trade_type': SBID,
                           # 'bid_price': bid_price, 'ask_price': ask_price,
                           'quantity': selling_coins, 'total': total_takings,
                           'fee': fee_loss}
        done = False
        if self._wallet['cash'] < 0.0001:
            done = True

        return done

    def get_current_trade(self):
        return self.curr_trade

    def get_wallet(self):
        return self._wallet

    def get_trade_history(self):
        return self.bookkeeping


class Accountant(object):
    '''This class represents the accountant.
    He is responsible for writing the logged transactions in a .json.
    So that you can see the training and the results in the viewer. '''

    def __init__(self, name):
        self.name = name
        # self.reader = open(json_report_path, 'rb', os.O_NONBLOCK)
        # self.writer = open(json_report_path, 'w', os.O_NONBLOCK)

    def append_trade_report(self, curr_trade):
        with open(json_report_path, 'a', os.O_NONBLOCK) as appender:
            # row = "{},\n".format(json.dumps(curr_trade))
            json.dump(curr_trade, appender)
            appender.write(',')

    async def report_history(self, trade_history):
        # trade_history = account.get_trade_history()
        f_path = json_report_path.format(int(time.time()))
        with open(f_path, 'w', os.O_NONBLOCK) as writer:
            json.dump(trade_history, writer)
        await asyncio.sleep(1)
        return True

    def request_trade_history(self):
        reader_ = open(json_report_path, 'r', os.O_NONBLOCK)
        with reader_ as reader:
            data = json.loads(reader.read())

        return data

    def request_last_n(self, N):
        reader_ = open(json_report_path, 'r', os.O_NONBLOCK)
        with reader_ as reader:
            data = json.loads(reader.read())

        return data[N:]

    def request_between(self, idx1, idx2):
        reader_ = open(json_report_path, 'r', os.O_NONBLOCK)
        with reader_ as reader:
            data = json.loads(reader.read())

        return data[idx1:idx2]
