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
from bokeh.models import HoverTool
from bokeh.charts import Donut


app = Flask(__name__)
tickers = pd.read_csv('https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/WIKI_tickers.csv')
ticker_symbols = tickers['quandl code']


def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]


def get_summary_data():
    dfiles = ['2014_Q1.csv', '2014_Q2.csv', '2014_Q3.csv', '2014_Q4.csv',
    '2015_Q1.csv', '2015_Q2.csv' , '2015_Q3.csv', '2015_Q4.csv',
    '2016_Q1.csv', '2016_Q2.csv', '2016_Q3.csv', '2016_Q4.csv']

    adf = []
    for file in dfiles:
        df = pd.read_csv("data/" + file)
        df['percent_total'] = df['percent_total'] * 100.0  # convert decimal to percent
        df = df.loc[df['failure_rate'] <=100]  # remove unreasonable failure rates
        df = df.loc[df['percent_total'] >=2] 
        del df['Unnamed: 0']  # delete malformed index row
        for cn in df.columns:
            df.rename(columns={cn: cn.replace("_", " ")}, inplace=True)  # clean up column names
        adf.append(df)
    time_strings = [x.replace(".csv", "").replace("_", " ") for x in dfiles]  # create clean time names
    return adf, time_strings

sd_df, time_strings = get_summary_data()

time_indexer = dict(zip(time_strings, range(len(time_strings))))

#print(time_strings)
#print(time_indexer)


def create_pie_plt(adf, time_index):
    df = adf[time_index]
    df = df.sort_values(by="percent total", ascending=False)
    d = Donut(df, label=['manufacturer','model'], values='percent total',text_font_size='12pt', hover_text='percent_total',
        plot_width=500, plot_height=500)
    #d.add_tools(HoverTool(tooltips= None, renderers=[d], mode='hline'))
    d.border_fill = None
    d.background_fill_color = "black"
    d.min_border_left = 0
    d.outline_line_width = 0
    d.outline_line_alpha = 0
    #d.outline_line_color = '#C1C1C1'
    #p.yaxis.text_color = '#C1C1C1'
    d.title.text_color = 'white'
    js = INLINE.render_js()
    css = INLINE.render_css()
    script, div = components(d)
    return script, div, js, css




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
    #print(js)
    css = INLINE.render_css()
    script, div = components(plot)
    return script, div, js, css

def generate_line_plot():
    x = np.linspace(0.1, 5, 100)
    p = figure(title="log axis example", y_axis_type="log", y_range=(0.001, 10**22),plot_width=400, plot_height=400)
    p.border_fill = "black"
    p.background_fill_color = "grey"
    p.min_border_left = 80
    p.outline_line_width = 7
    p.outline_line_alpha = 0.3
    p.outline_line_color = "white"
    #p.yaxis.text_color = '#C1C1C1'
    p.title.text_color = '#C1C1C1'
    #p.xaxis.major_tick_line_width = 'white'
    #p.xaxis.minor_tick_line_color = '#C1C1C1'
    #p.yaxis.text_color = '#C1C1C1'
    #p.axis_label.text_color = '#C1C1C1'
    #p.major_label.text_color = '#C1C1C1'
    #p.xaxis.text_color = '#C1C1C1'


    #p.xgrid.grid_line_color = 'white'
    #p.ygrid.grid_line_color = 'white'
    p.xgrid.grid_line_alpha = 0.1
    p.ygrid.grid_line_alpha = 0.1

    p.line(x, np.sqrt(x), legend="y=sqrt(x)", line_color="tomato", line_dash="dotdash")
    p.line(x, x, legend="y=x")
    p.circle(x, x, legend="y=x")
    p.line(x, x**2, legend="y=x**2")
    p.circle(x, x**2, legend="y=x**2", fill_color=None, line_color="olivedrab")


    cr = p.circle(x, x**2, size=20,
                fill_color="grey", hover_fill_color="white",
                fill_alpha=0.05, hover_alpha=0.3,
                line_color=None, hover_line_color="white")
    p.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='hline'))



    p.legend.location = "top_left"

    #output_file("logplot.html", title="log plot example")
    js = INLINE.render_js()
    css = INLINE.render_css()
    script, div = components(p)
    return script, div, js, css





from bokeh.layouts import column
from bokeh.models import CustomJS, ColumnDataSource, Slider
def generate_slider_plot():
    x = [x*0.005 for x in range(0, 200)]
    y = x

    source = ColumnDataSource(data=dict(x=x, y=y))

    plot = figure(plot_width=400, plot_height=400)
    plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

    callback = CustomJS(args=dict(source=source), code="""
    var data = source.data;
    var f = cb_obj.value
    x = data['x']
    y = data['y']
    for (i = 0; i < x.length; i++) {
        y[i] = Math.pow(x[i], f)
    }
    source.trigger('change');
    """)

    slider = Slider(start=0.1, end=4, value=1, step=.1, title="power")
    slider.js_on_change('value', callback)


    layout = column(slider, plot)
    js = INLINE.render_js()
    css = INLINE.render_css()
    script, div = components(layout)
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

                line_script, line_div, js, css = generate_line_plot()
                html = flask.render_template('index.html', place_holder="Enter a stock symbol",
                                             line_plot_script=line_script, line_plot_div=line_div,
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
        script, div, js, css = generate_line_plot()


        pie_script, pie_div, js, css = create_pie_plt(sd_df, time_indexer['2016 Q1'])
        slider_script, slider_div, js, css = generate_slider_plot()
        html = flask.render_template('index.html', place_holder="Enter a stock.",
                                             line_plot_script=pie_script, line_plot_div=pie_div, js_resources=js, css_resources=css,
                                             slider_plot_script=slider_script, slider_plot_div=slider_div, 
                                             measure=measure, open=plt_open, close=plt_close, adj_open=plt_adj_open,
                                             adj_close=plt_adj_close)
        #html = flask.render_template('index.html', place_holder="Enter a stock symbol",
        #                             js_resources=js_resources, css_resources=css_resources,
        #                             measure=measure, open=plt_open, close=plt_close, adj_open=plt_adj_open,
        #                             adj_close=plt_adj_close)

        return html


if __name__ == '__main__':
    app.run(port=33507)








