from flask import Flask, render_template, request, redirect, Markup
import pandas as pd
import flask
import requests
from bokeh.plotting import figure
from bokeh.embed import components
#from bokeh.models import NumeralTickFormatter
import numpy as np
#import datetime
from bokeh.resources import INLINE
from bokeh.models import HoverTool
#from bokeh.charts import Donut
import km_plot
#import pie_plot
import load_data
import donut_plot



app = Flask(__name__)

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

adf, time_strings, seagate_color_dict, hitachi_color_dict, hgst_color_dict, western_color_dict = load_data.get_summary_data()
# time_indexer = dict(zip(time_strings, range(len(time_strings))))
pie_plot = donut_plot.generate_pie_plots(adf, time_strings, seagate_color_dict, hitachi_color_dict, hgst_color_dict, western_color_dict)
pie_script, pie_div = components(pie_plot)



kms, models = km_plot.load_survival_data()
surv_plot = km_plot.generate_km_plot(kms, models)
js = INLINE.render_js()
css = INLINE.render_css()
surv_script, surv_div = components(surv_plot)



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
    #js = INLINE.render_js()
    #css = INLINE.render_css()
    #script, div = components(layout)
    return layout

slider_script, slider_div = components(generate_slider_plot())

@app.route('/', methods=['GET', 'POST'])
def index():
    #measure = getitem(request.form, 'Measure', '6months')
    #plt_open = getitem(request.form, 'open', "0")
    #plt_close = getitem(request.form, 'close', "0")
    #plt_adj_open = getitem(request.form, 'adj_open', "0")
    #plt_adj_close = getitem(request.form, 'adj_close', "0")
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    #print("request.from", request.form)
    #if request.method == 'POST':
    try: 
            html = flask.render_template('index.html', js_resources = js_resources, css_resources = css_resources,
                surv_plot_script = surv_script,  surv_plot_div = surv_div,
                pie_plot_script = pie_script, pie_plot_div = pie_div,
                slider_plot_script = slider_script, slider_plot_div = slider_div)
            return html
    except:
            html = flask.render_template('index.html', place_holder="Invalid symbol")
            return html


if __name__ == '__main__':
    app.run(port=33507)








