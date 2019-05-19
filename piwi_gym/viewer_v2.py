from dash import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import dash_daq as daq
from dash.dependencies import Input, Output, State
from piwi_gym.configs import *
import os
import json


class Viewer(object):
    def __init__(self, name):
        self.app = dash.Dash(__name__)
        self.app.css.config.serve_locally = True
        self.app.scripts.serve_locally = True
        self.server = self.app.server
        self.curr_idx = 0
        self.curr_cash = 0
        self.curr_assets = 0
        self.curr_loss = 0
        self.curr_profit = 0
        self.trades = []
        self.curr_window = []
        self.disable = 9999999
        self.load_trade_report()
        self.serve_layout()
        self.init_callbacks()
        self.run_app()

    def load_trade_report(self):
        with open(json_report_path, 'r', os.O_NONBLOCK) as reader:
            data = json.load(reader)

        self.trades = data

    def serve_layout(self):
        page_layout = html.Div(id='page', children=[
            # banner
            html.Div(
                className='page-title',
                title='Piwi Gym',
                children=['piwi gym']
            ),
            self.get_graph_container(),
            self.get_power_box(),
            self.get_account_box(),

        ])
        self.app.layout = html.Div(id='main', children=page_layout)

        return True

    def init_callbacks(self):
        self.create_graphupdate_callback()
        self.create_cashupdate_callback()
        self.create_assetsupdate_callback()
        self.create_lossupdate_callback()
        self.create_profitupdate_callback()
        self.create_update_interval_callback()

    def get_graph_container(self):
        # plot
        container = html.Div(
            id='graph-container',
            children=[
                html.Div(
                    children=[
                        dcc.Graph(id='tick-readings', animate=False),
                        dcc.Interval(id='tick-reading-interval',
                                     interval=self.disable,
                                     n_intervals=0)
                    ]
                )
            ]
        )
        return container

    def get_account_box(self):
        # status box
        acc_box = html.Div(
            id='account-box',
            children=[
                html.Div(
                    # id='account-balances',
                    children=[
                        html.Div(
                            className='status-box-title',
                            children=[
                                "cash"
                            ]
                        ),
                        daq.LEDDisplay(
                            id='cash-display',
                            value='1.001',
                            color=colors['accent'],
                            backgroundColor=colors['background'],
                            size=18
                        ),
                        html.Div(
                            className='status-box-title',
                            children=[
                                "assets"
                            ]
                        ),
                        daq.LEDDisplay(
                            id='coins-display',
                            value='5.0001',
                            color=colors['accent'],
                            backgroundColor=colors['background'],
                            size=18
                        ),
                        html.Div(
                            className='status-box-title',
                            children=[
                                "loss"
                            ]
                        ),
                        daq.LEDDisplay(
                            id='total-costs',
                            value='1.0',
                            color=colors['ultra_purp'],
                            backgroundColor=colors['background'],
                            size=18
                        ),
                        html.Div(
                            className='status-box-title',
                            children=[
                                "profit"
                            ]
                        ),
                        daq.LEDDisplay(
                            id='total-earnings',
                            value='1.0',
                            color=colors['ultra_purp'],
                            backgroundColor=colors['background'],
                            size=18
                        ),
                    ]
                )
            ]
        )
        return acc_box

    def get_power_box(self):
        # power box
        pwr_box = html.Div(
            id='power-box',
            children=[
                # power button
                html.Div(
                    id='power-button-container',
                    title='Turn the power on to begin viewing the data and controlling \
                                                    the spectrometer.',
                    children=[
                        daq.PowerButton(
                            id='power-button',
                            size=70,
                            color=colors['accent'],
                            on=False
                        ),
                    ],
                ),

            ]
        )
        return pwr_box

    def get_line_traces(self, traces, idxs_, prices_, color_):

        traces.append(go.Scatter(
            x=idxs_,
            y=prices_,
            name='ask_price',
            mode='lines',
            line={
                'width': 1,
                'color': color_
            }
        )
        )
        return traces

    def get_marker_trace(self, traces, idxs_, act_prices_, marker_sizes, action_colors):
        traces.append(go.Scatter(
            x=idxs_,
            y=act_prices_,
            name='action_price',
            mode='markers',
            opacity=0.9,
            marker={
                'size': marker_sizes,
                'color': action_colors,
                'line': {'width': 1,
                         'color': [colors['ultra_purp'] if col_ == colors['accent'] else colors['accent'] for col_ in
                                   action_colors]}
            },
        ))
        return traces

    def get_trace_layout(self):
        x_axis, y_axis = self.format_x_y_axis()
        layout = go.Layout(
            height=600,
            font={
                'family': 'Helvetica Neue, sans-serif',
                'size': 12,
                'color': colors['ultra_purp'],
            },
            margin={
                't': 20,
            },
            titlefont={
                'family': 'Helvetica, sans-serif',
                'color': colors['primary'],
                'size': 26,
            },
            xaxis=x_axis,
            yaxis=y_axis,
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            legend=dict(orientation='h',
                        font={
                            'family': 'Helvetica Neue, sans-serif',
                            'size': 12,
                            'color': colors['accent']
                        }
                        )
        )
        return layout

    def format_x_y_axis(self):
        x_axis = {
            'title': 'time (t)',
            'titlefont': {
                'family': 'Helvetica, sans-serif',
                'color': colors['accent']
            },
            'tickfont': {
                'color': colors['accent']
            },
            'dtick': 50,
            'color': colors['secondary'],
            'gridcolor': colors['grid-colour'],
            'autorange': True
        }
        y_axis = {
            'title': 'price (btc)',
            'titlefont': {
                'family': 'Helvetica, sans-serif',
                'color': colors['accent']
            },
            'tickfont': {
                'color': colors['accent']
            },
            'color': colors['secondary'],
            'gridcolor': colors['grid-colour'],
            'autorange': True
        }

        return x_axis, y_axis

    # callbacks
    def create_graphupdate_callback(self):
        self.app.callback(Output('tick-readings', 'figure'),
                          state=[State('power-button', 'on')],
                          inputs=[Input('tick-reading-interval', 'n_intervals')])(self.update_plot)

    def create_cashupdate_callback(self):
        self.app.callback(Output('cash-display', 'value'),
                          inputs=[Input('tick-reading-interval', 'n_intervals')])(self.update_cash)

    def create_assetsupdate_callback(self):
        self.app.callback(Output('coins-display', 'value'),
                          inputs=[Input('tick-reading-interval', 'n_intervals')])(self.update_assets)

    def create_lossupdate_callback(self):
        self.app.callback(Output('total-costs', 'value'),
                          inputs=[Input('tick-reading-interval', 'n_intervals')])(self.update_total_loss)

    def create_profitupdate_callback(self):
        self.app.callback(Output('total-earnings', 'value'),
                          inputs=[Input('tick-reading-interval', 'n_intervals')])(self.update_total_profit)

    def create_update_interval_callback(self):
        self.app.callback(Output('tick-reading-interval', 'interval'),
                          inputs=[Input('power-button', 'on')])(self.update_interval)


    def update_plot(self, n, on):
        traces = []
        idxs_ = []
        ask_prices_ = []
        bid_prices_ = []
        act_prices_ = []
        act_colors_ = []
        marker_sizes = []
        window_len = 100

        if on:
            if n > window_len:
                tr_history = self.trades[n - window_len: n]
            else:
                tr_history = self.trades[:n]

            self.update_curr_info(tr_history)

            for t_h in tr_history:
                ask_prices_.append(t_h[ASK])
                bid_prices_.append(t_h[BID])
                total = round(t_h[TOT], 8)

                if t_h[TYPE] == 'sell_bid':
                    act_prices_.append(t_h[BID])
                    act_colors_.append(colors['ultra_purp'])
                elif t_h[TYPE] == 'buy_ask':
                    act_prices_.append(t_h[ASK])
                    act_colors_.append(colors['accent'])
                elif t_h[TYPE] == 'hold':
                    act_prices_.append((t_h[ASK] + t_h[BID]) / 2)
                    act_colors_.append(colors['vivid_lime'])
                marker_sizes.append(9 + int(total))
                idxs_.append(t_h[CIDX])
        else:
            ask_prices_ = [0.001 for i in range(0, 50)]
            bid_prices_ = [0.0011 for j in range(0, 50)]
            idxs_ = [k for k in range(0, 50)]

        traces = self.get_line_traces(traces, idxs_, ask_prices_, colors['ultra_purp'])
        traces = self.get_line_traces(traces, idxs_, bid_prices_, colors['accent'])
        if (on):
            traces = self.get_marker_trace(traces, idxs_, act_prices_,
                                           marker_sizes, act_colors_)

        layout = self.get_trace_layout()
        return {'data': traces, 'layout': layout}

    def update_curr_info(self, history):
        self.curr_cash = history[-1]['wallet']['cash']
        self.curr_assets = history[-1]['wallet']['coins']
        self.curr_loss = history[-1]['wallet']['loss']
        self.curr_profit = history[-1]['wallet']['profit']

    def update_cash(self, n):
        cash = 1.0
        if n > 0:
            cash = self.curr_cash

        return round(cash, 7)

    def update_assets(self, n):
        coins = 1.0
        if n > 0:
            coins = self.curr_assets

        return round(coins, 7)

    def update_total_profit(self, n):
        profit = 0.0
        if n > 0:
            profit = self.curr_profit

        return round(profit, 7)

    def update_total_loss(self, n):
        costs = 0.0
        if n > 0:
            costs = self.curr_loss
        return round(costs, 7)

    def update_interval(self, on):
        if on:
            return 500
        else:
            return self.disable

    def run_app(self, debug_=True):
        self.app.run_server(debug=debug_)


viewer = Viewer('gym_tv')
viewer.run_app(False)
