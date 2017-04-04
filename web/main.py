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
#tickers = pd.read_csv('https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/WIKI_tickers.csv')
#ticker_symbols = tickers['quandl code']


def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]


def generate_plot(title_one, title_two, var1, var2):
    #end_date = datetime.datetime.now()
    #if time_measure == '1month':
    #    start_date = end_date + datetime.timedelta(-32)
    #if time_measure == '6months':
    #    start_date = end_date + datetime.timedelta(-186)
    #if time_measure == '1year':
    #    start_date = end_date + datetime.timedelta(-365)
    #if time_measure == '5years':
    #    start_date = end_date + datetime.timedelta(-365 * 5)
    #if time_measure == 'max':
    #    start_date = end_date + datetime.timedelta(-365 * 100)

    if var1 == 'state1':
    	data = pd.readCSV('junk1.csv')
    if var1 == 'state2':
    	data = pd.readCSV('junk2.csv')
	
    plot = figure(title=name, tools='wheel_zoom, box_zoom, save, reset',
                  responsive=True, plot_width=450, plot_height=400)#, x_axis_type='datetime')
    plot.toolbar.logo = None
    if var2[0] == '1':
        plot.line(df['alpha'], df['beta'], line_width=2, color="blue", legend='beta')

    if var2[1] == '1':
        plot.line(df['alpha'], df['gamma'], closing_price, line_width=2, color="green", legend='gamma')

    plot.legend.location = 'top_left'
    plot.legend.background_fill_alpha = 0.1
    #plot.yaxis[0].formatter = NumeralTickFormatter(format='$0.00')
    js = INLINE.render_js()
    css = INLINE.render_css()
    script, div = components(plot)
    return script, div, js, css


@app.route('/', methods=['GET', 'POST'])
def index():

    #default values
    current_var1 = getitem(request.form, 'var1', 'state1')
    current_var2_0 = getitem(request.form, 'var2', '0')
    current_var2_1 = getitem(request.form, 'var2', "0")
    #plt_adj_open = getitem(request.form, 'adj_open', "0")
    #plt_adj_close = getitem(request.form, 'adj_close', "0")
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    print("request.from", request.form)
    if request.method == 'POST':# and 'symbol' in request.form:
        #sym = request.form['symbol'].upper()
        #if 'WIKI/' + sym in ticker_symbols.values:
        try:
                #stock = tickers.loc[ticker_symbols == 'WIKI/' + sym, 'name'].values[0]
        	script, div, js, css = generate_plot('title 1', 'title2', current_var1,
                                                     [current_var2_0,current_var2_1])
                html = flask.render_template('index.html', place_holder="request.method was post",
                                             plot_script=script, plot_div=div, js_resources=js, css_resources=css,
                                             html_var1=current_var1, html_var2_0=current_var2_0, html_var2_1=current_var2_1)
                return html
            except:
                html = flask.render_template('index.html', place_holder="Exception in try",
                                             plot_script=script, plot_div=div, js_resources=js, css_resources=css,
                                             html_var1=current_var1, html_var2_0=current_var2_0, html_var2_1=current_var2_1)
                #html = flask.render_template('index.html', place_holder="Fail. Something went wrong",
                #                             js_resources=js_resources, css_resources=css_resources,
                #                             open=plt_open, close=plt_close, adj_open=plt_adj_open,
                #                             adj_close=plt_adj_close)
                return html
        else:
            html = flask.render_template('index.html', place_holder="Method was not post",
                                             plot_script=script, plot_div=div, js_resources=js, css_resources=css,
            #html = flask.render_template('index.html', place_holder="Invalid symbol",
            #                             js_resources=js_resources, css_resources=css_resources,
            #                             measure=measure, open=plt_open, close=plt_close, adj_open=plt_adj_open,
            #                             adj_close=plt_adj_close)
            return html
    #else:
    #    html = flask.render_template('index.html', place_holder="Enter a stock symbol",
        #                             js_resources=js_resources, css_resources=css_resources,
       #                              measure=measure, open=plt_open, close=plt_close, adj_open=plt_adj_open,
     #                                adj_close=plt_adj_close)
      #  return html


if __name__ == '__main__':
    app.run(port=33507)








