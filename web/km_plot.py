import os
import numpy as np
import pandas as pd
from bokeh.plotting import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.io import push_notebook, show, output_notebook
from bokeh.models import Legend
from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Select, Toggle, RadioButtonGroup, Button
from bokeh.layouts import row, widgetbox

def load_survival_data():
    INPUT_DIR = "data"
    kms = []
    models = []
    for data_file in os.listdir(INPUT_DIR):
        if data_file.split('.')[1] == 'csv' and data_file.split('_')[0] == 'kmfit':
            km_fit = pd.read_csv(INPUT_DIR + "/" + data_file, header=0)
            kms.append(km_fit)
            model_name =  data_file.split('.')[0]
            model_name =  model_name.split('kmfit_')[1]
            model_name =  model_name.replace("_", " ")
            models.append(model_name)
    return kms, models

def generate_km_plot(kms, models, color_dict):
    surv_plt1 = figure(title="Survival Analysis", tools=['hover,box_zoom,wheel_zoom,save,reset'])
    hover = surv_plt1.select(dict(type=HoverTool))
    hover.tooltips = [
        ("Model ", "@model"),
        ("Time ", "@timeline"),
        ("survival fraction ", "@km_surv"),
        ("upper 95% bound ", "@surv_upper"),
        ("lower 95% bound ", "@surv_lower")
        ]
    if len(kms) > 1:
        hover.mode = 'mouse'
    else: 
        hover.mode = 'vline'
    
    km_colors = ['#1a1334', '#03c383', '#fbbf45', '#ed0345' ,  '#26294a', '#aad962', '#01545a', '#ef6a32','#017351',
              '#a12a5e', '#710162', '#110141']
    #km_colors = [str(color_dict[model_key]) if model_key in color_dict else 'grey' for model_key in models]

    n = 0
    surv_plt_objs1 = []
    surv_plt_objs2 = []
    for km in kms:
        model = models[n]
        time = km['time'] 
        surv = km['surv'] 
        surv_upper = km['surv_lower']  
        surv_lower = km['surv_upper'] 
        band_x = np.append(time, time[::-1])
        band_y = np.append(surv_upper, surv_lower[::-1])
        source = ColumnDataSource(
            data=dict(
                timeline=[i for i in time],
                km_surv=[i for i in surv],
                model=[models[n] for i in time],
                surv_lower=[i for i in surv_lower],
                surv_upper=[i for i in surv_upper]
            )
        )
        tmp = surv_plt1.patch(band_x, band_y, color=km_colors[n], fill_alpha=0.2)
        surv_plt_objs1.append(tmp)
        tmp = surv_plt1.line('timeline', 'km_surv', line_width = 2, alpha=.8, source = source, legend=models[n], color=km_colors[n])
        surv_plt_objs2.append(tmp)
        n += 1

    surv_plt1.xaxis.axis_label = 'Time (Years)'
    surv_plt1.yaxis.axis_label = 'Kaplan-Meier Estimation (survival fraction)'
    
    # grid styles
    surv_plt1.toolbar.logo = None
    surv_plt1.grid.grid_line_alpha = 0
    surv_plt1.ygrid.band_fill_color = None#"grey"
    surv_plt1.ygrid.band_fill_alpha = 0.1
    surv_plt1.x_range.range_padding = 0
    surv_plt1.legend.location = "bottom_left"
    surv_plt1.plot_height = 700
    surv_plt1.plot_width = 790
    #surv_plt1.border_fill_color = "black"
    #surv_plt1.background_fill_color = "white"
    surv_plt1.min_border_left = 80
    surv_plt1.outline_line_width = 1
    surv_plt1.outline_line_alpha = 0.3
    surv_plt1.xaxis.minor_tick_line_color = None#'N'
    surv_plt1.yaxis.minor_tick_line_color = None#'#C1C1C1'
    #surv_plt1.xaxis.major_label_text_color = 'white'
    surv_plt1.y_range = Range1d(0.0, 1.02)

    code1 = '''\
    object1.visible = toggle.active
    object2.visible = toggle.active
    '''

    #Toggle possible attributes are:
    # active, button_type, callback, css_classes, disabled, height, icon, js_callbacks, label, name, sizing_mode, tags or width
    callbacks = []
    toggles = []
    for i in range(len(models)):
            callbacks.append(CustomJS.from_coffeescript(code=code1, args={}))
            km_color = km_colors[i].lstrip("#")
            style_class = ('bk-' + km_color, 'bk-' + km_color)
            toggles.append(Toggle(label=models[i], button_type="success", callback=callbacks[i], css_classes =style_class)) 
            callbacks[i].args = {'toggle': toggles[i], 'object1': surv_plt_objs1[i],  'object2': surv_plt_objs2[i]}

    togs = [t for t in list(toggles)]
    controls = widgetbox(togs, width=190)
    layout = row(controls, surv_plt1)
    return layout

stand_alone_test = False
if stand_alone_test:
    import load_data
    from bokeh.io import show
    from bokeh.io import show
    adf, time_strings, color_dict, colors = load_data.get_summary_data()
    surv, m = load_survival_data()
    dplt = generate_km_plot(surv, m, color_dict)
    show(dplt)