from flask import Flask, render_template, request, redirect, Markup
import pandas as pd
import flask
import requests
from bokeh.plotting import figure
from bokeh.embed import components
import numpy as np
from bokeh.resources import INLINE
from bokeh.models import HoverTool
import km_plot
import load_data
import donut_plot
import bar_plot
import table_plot
import omni_plot


app = Flask(__name__)

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

adf, time_strings, color_dict, colors = load_data.get_summary_data()
# time_indexer = dict(zip(time_strings, range(len(time_strings))))

pie_plot = donut_plot.generate_pie_plots(adf, time_strings, color_dict, colors)
pie_script, pie_div = components(pie_plot)

table_plot = table_plot.generate_table_plots(adf, time_strings, color_dict, colors)
table_script, table_div = components(table_plot)

bar_plot = bar_plot.generate_bar_plots(adf, time_strings, color_dict, colors)
bar_script, bar_div = components(bar_plot)

c1, sdf, hcols = omni_plot.gather_stat_data(adf, color_dict)

om_plot = omni_plot.generate_summary_plot(c1, hcols)
omni_script, omni_div = components(om_plot)

box_plot = omni_plot.generate_box_plot(sdf, colors)
box_script, box_div = components(box_plot)

choose_plot = omni_plot.generate_performance_plot(c1, hcols)
choose_script, choose_div = components(choose_plot)

kms, models = km_plot.load_survival_data()
surv_plot = km_plot.generate_km_plot(kms, models, color_dict)

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
    return layout

slider_script, slider_div = components(generate_slider_plot())

@app.route('/', methods=['GET', 'POST'])
def index():
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    try: 
            html = flask.render_template('index.html', js_resources = js_resources, css_resources = css_resources,
                choose_plot_script = choose_script, choose_plot_div = choose_div,
                box_plot_script = box_script, box_plot_div = box_div,
                omni_plot_script = omni_script, omni_plot_div = omni_div,
                surv_plot_script = surv_script,  surv_plot_div = surv_div,
                pie_plot_script = pie_script, pie_plot_div = pie_div,
                table_plot_script = table_script, table_plot_div = table_div,
                bar_plot_script = bar_script, bar_plot_div = bar_div,
                slider_plot_script = slider_script, slider_plot_div = slider_div)
            return html
    except:
            html = flask.render_template('index.html', place_holder="Error in flask, python, bokeh, java pipeline")
            return html

if __name__ == '__main__':
    app.run(port=33507)








