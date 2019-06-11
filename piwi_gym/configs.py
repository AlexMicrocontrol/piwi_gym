import os
from glob import glob

cwd = os.path.dirname(os.path.abspath(__file__))

# Viewer
color_path = glob('{}*/assets/colors.txt'.format(cwd))
# Trade Report
json_report_path = '{}/data/account_reports/trade_report_{}.json'.format(cwd, '{}')
train_file = glob('{}*/data/training/BTC_ETH_v1_Optimal_Actions.csv'.format(cwd))
sequence_len = 24
tt_split = 0.85
batch_size = 12
train_epochs = 5
shouldNormalize = False
doFeatureEng = False
columns = ['bid', 'ask',
           'sell_vol', 'buy_vol',
           # 'return', 'action'
           ]
win_shift = 1

start_cash = 3
start_assets = 3
asset_type = 'BTC-ETH'
buy_limit_pct = 0.15
sell_limit_pct = 0.9
trading_fee_pct = 0.01

colors = {}
with open(color_path[0], 'r') as f:
    for line in f.readlines():
        colors[line.split(' ')[0]] = line.split(' ')[1].strip('\n')

# ACTIONS
HOLD, BUY, SELL = [0, 1, 2]

ASK = 'ask_price'
BID = 'bid_price'
TOT = 'total'
CIDX = 'curr_idx'
TYPE = 'trade_type'
SBID = 'sell_bid'
BASK = 'buy_ask'
hLD = 'hold'
CSH = 'cash'
ASST = 'coins'
LSS = 'loss'
PFT = 'profit'

SHOW_ONLY_N_TICKS = 100

REWARD_STRAT = "Cash"
#
