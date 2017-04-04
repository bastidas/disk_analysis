from flask import Flask, render_template, request, redirect, Markup
import pandas as pd
import flask
import requests
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import NumeralTickFormatter
import numpy as np
import datetime
from bokeh.resources import INLINE

app = Flask(__name__)
tickers = pd.read_csv('https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/WIKI_tickers.csv')
ticker_symbols = tickers['quandl code']


def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]


def generate_plot(symbl, name, time_measure, data_series):
    end_date = datetime.datetime.now()
    if time_measure == '1month':
        start_date = end_date + datetime.timedelta(-32)
    if time_measure == '6months':
        start_date = end_date + datetime.timedelta(-186)
    if time_measure == '1year':
        start_date = end_date + datetime.timedelta(-365)
    if time_measure == '5years':
        start_date = end_date + datetime.timedelta(-365 * 5)
    if time_measure == 'max':
        start_date = end_date + datetime.timedelta(-365 * 100)

    api_url = 'https://www.quandl.com/api/v3/datasets/WIKI/%s.json?api_key=t-drH_WSpLdRenh1o86E&start_date=%s&end_date=%s' \
              % (symbl, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=2))
    raw_json = session.get(api_url).json()['dataset']

    df = pd.DataFrame({'date': [x[0] for x in raw_json['data']], 'close': np.array([x[4] for x in raw_json['data']]), })
    df['date'] = pd.to_datetime(df['date'])
    plot = figure(title=name, tools='wheel_zoom, box_zoom, save, reset',
                  responsive=True, plot_width=750, plot_height=400, x_axis_type='datetime')
    plot.toolbar.logo = None
    if data_series[0] == '1':
        opening_price = np.array([x[1] for x in raw_json['data']])
        plot.line(df['date'], opening_price, line_width=2, color="blue", legend='Opening price')

    if data_series[1] == '1':
        closing_price = np.array([x[4] for x in raw_json['data']])
        plot.line(df['date'], closing_price, line_width=2, color="green", legend='Closing price')

    if data_series[2] == '1':
        opening_adj_price = np.array([x[8] for x in raw_json['data']])
        plot.line(df['date'], opening_adj_price, line_width=2, color="grey", legend='Adjusted opening price')

    if data_series[3] == '1':
        closing_adj_price = np.array([x[11] for x in raw_json['data']])
        plot.line(df['date'], closing_adj_price, line_width=2, color="black", legend='Adjusted closing price')
    plot.legend.location = 'top_left'
    plot.legend.background_fill_alpha = 0.1
    plot.yaxis[0].formatter = NumeralTickFormatter(format='$0.00')
    js = INLINE.render_js()
    css = INLINE.render_css()
    script, div = components(plot)
    return script, div, js, css


@app.route('/', methods=['GET', 'POST'])
def index():
    measure = getitem(request.form, 'Measure', '6months')
    plt_open = getitem(request.form, 'open', "0")
    plt_close = getitem(request.form, 'close', "0")
    plt_adj_open = getitem(request.form, 'adj_open', "0")
    plt_adj_close = getitem(request.form, 'adj_close', "0")
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    print("request.from", request.form)
    if request.method == 'POST' and 'symbol' in request.form:
        sym = request.form['symbol'].upper()
        if 'WIKI/' + sym in ticker_symbols.values:
            try:
                stock = tickers.loc[ticker_symbols == 'WIKI/' + sym, 'name'].values[0]
                script, div, js, css = generate_plot(sym, stock, measure,
                                                     [plt_open, plt_close, plt_adj_open, plt_adj_close])
                html = flask.render_template('index.html', place_holder="Enter a stock symbol",
                                             plot_script=script, plot_div=div, js_resources=js, css_resources=css,
                                             measure=measure, open=plt_open, close=plt_close, adj_open=plt_adj_open,
                                             adj_close=plt_adj_close)
                return html
            except:
                html = flask.render_template('index.html', place_holder="Fail. Something went wrong",
                                             js_resources=js_resources, css_resources=css_resources,
                                             open=plt_open, close=plt_close, adj_open=plt_adj_open,
                                             adj_close=plt_adj_close)
                return html
        else:
            html = flask.render_template('index.html', place_holder="Invalid symbol",
                                         js_resources=js_resources, css_resources=css_resources,
                                         measure=measure, open=plt_open, close=plt_close, adj_open=plt_adj_open,
                                         adj_close=plt_adj_close)
            return html
    else:
        html = flask.render_template('index.html', place_holder="Enter a stock symbol",
                                     js_resources=js_resources, css_resources=css_resources,
                                     measure=measure, open=plt_open, close=plt_close, adj_open=plt_adj_open,
                                     adj_close=plt_adj_close)
        return html


if __name__ == '__main__':
    app.run(port=33507)








