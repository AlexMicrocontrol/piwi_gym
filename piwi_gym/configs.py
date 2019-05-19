# Viewer
color_path = 'assets/colors.txt'
# Trade Report
json_report_path = '/data/account_reports/trade_report_{}.json'
train_file = '/data/training/BTC_ETH_v1_Optimal_Actions.csv'
sequence_len = 12
tt_split = 0.85
batch_size = 12
train_epochs = 5
shouldNormalize = False
doFeatureEng = False

start_cash = 3
start_assets = 3
asset_type = 'BTC-ETH'
buy_limit_pct = 0.15
sell_limit_pct = 0.9
trading_fee_pct = 0.01

colors = {}
with open(color_path, 'r') as f:
    for line in f.readlines():
        colors[line.split(' ')[0]] = line.split(' ')[1].strip('\n')

# ACTIONS
HOLD, BUY, SELL = [0, 1, 2]

ASK = 'ask_price'
BID = 'bid_price'
TOT = 'total'
CIDX = 'curr_idx'
TYPE = 'trade_type'
CSH = 'cash'
ASST = 'coins'
LSS = 'loss'
PFT = 'profit'

SHOW_ONLY_N_TICKS = 100
#
