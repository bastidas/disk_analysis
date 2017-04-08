from bokeh.models import HoverTool
#from bokeh.io import push_notebook, show, output_notebook
#from bokeh.layouts import row
from bokeh.plotting import figure

def km_bokeh_plot(km, model):
    s = km.survival_function_
    ci = km.confidence_interval_
    time = s['KM_estimate'].index
    surv = s['KM_estimate'].values
    surv_upper = ci['KM_estimate_upper_0.95'].values
    surv_lower = ci['KM_estimate_lower_0.95'].values
    band_x = np.append(time, time[::-1])
    band_y = np.append(surv_upper, surv_lower[::-1])
    surv_plt1 = figure(x_axis_type='datetime', title="Survival Analysis")
    surv_plt1.patch(band_x, band_y, color='#7570B3', fill_alpha=0.2)
    sline = surv_plt1.line(time, surv, legend=model, color='navy')#,  text_font_size ='12pt')

    surv_plt1.add_tools(HoverTool(tooltips=None, renderers=[sline], mode='hline'))
    
    #surv_plt1.grid.grid_line_alpha = 0.4
    surv_plt1.x_range.range_padding = 0
    surv_plt1.grid.grid_line_alpha = 0
    surv_plt1.xaxis.axis_label = 'Timeline'
    surv_plt1.yaxis.axis_label = 'Kaplan Meier Survival'
    #surv_plt1.ygrid.band_fill_color = "grey"
    #surv_plt1.ygrid.band_fill_alpha = 0.1
    surv_plt1.legend.location = "bottom_left"
    surv_plt1.plot_height = 500
    surv_plt1.plot_width = 700
    surv_plt1.border_fill_color = "black"
    surv_plt1.background_fill_color = "white"
    surv_plt1.min_border_left = 80
    surv_plt1.outline_line_width = 1
    surv_plt1.outline_line_alpha = 0.3
    surv_plt1.outline_line_color = "white"
    surv_plt1.xaxis.axis_label_text_color="white"
    surv_plt1.yaxis.axis_label_text_color="white"
    surv_plt1.xaxis.major_tick_line_color = 'white'
    surv_plt1.yaxis.major_tick_line_color = 'white'
    surv_plt1.xaxis.minor_tick_line_color = '#C1C1C1'
    surv_plt1.yaxis.minor_tick_line_color = '#C1C1C1'
    surv_plt1.xaxis.major_label_text_color = 'white'
    surv_plt1.yaxis.major_label_text_color = 'white'
    surv_plt1.title.text_color = 'white'

    #upper and lower 95% confidence intervals shown
    show(surv_plt1)
         
model = 'model name'
km_bokeh_plot(km, model)

