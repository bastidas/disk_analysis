from bokeh.charts import Bar, output_file, show
from bokeh.sampledata.autompg import autompg as df
#from math import pi, sin, cos
#from bokeh.models.glyphs import Wedge, AnnularWedge, ImageURL, Text
from bokeh.models import ColumnDataSource, Plot, Range1d
from bokeh.palettes import brewer
from bokeh.models.widgets import Panel, Tabs
from bokeh.layouts import layout, row
from bokeh.models import HoverTool






def generate_single_bar(df, time_str, color_dict, colors):

	df = df[df.percent_total >= 3]
	title = "Failure Rate " + time_str
	fill = [color_dict[model_key] if model_key in color_dict else 'grey' for model_key in df.model]
	source = ColumnDataSource(dict(color=[c for c in df['color']],
		model=[m for m in df['model']],
		failure_rate=[f for f in df['failure_rate']],
		count=[co for co in df['count']]))

	plot = Bar(df, 'model', values='failure_rate', title=title, source=source, tools=['hover'],color='color', legend=None)
	# outline_line_color="color", border_fill_color='color', 
	hover = plot.select(dict(type=HoverTool))
	hover.tooltips = [
        ("Model ", "@model"),
        ("Failure rate ", "@y"),
        ("Number of drives", "@count")        #("Time ", "@timeline"),
        ]
	hover.mode = 'mouse'
	plot.xaxis.axis_label = 'Model Serial Number'
	plot.yaxis.axis_label = 'Naive Failure Rate'
	plot.title_text_font_size="18px"
	plot.grid.grid_line_alpha = 0
	plot.ygrid.grid_line_color = None
	plot.toolbar.logo = None
	plot.outline_line_width = 0
	plot.outline_line_color = "white"
	plot.plot_height = 600
	plot.plot_width = 800
	plot.xaxis.major_tick_line_color = None
	plot.yaxis.major_tick_line_color = None
	plot.xaxis.axis_line_width = 2
	plot.yaxis.axis_line_width = 2
	plot.title.text_font_size = '16pt'
	plot.xaxis.axis_label_text_font_size = "14pt"
	plot.xaxis.major_label_text_font_size = "14pt"
	plot.yaxis.axis_label_text_font_size = "14pt"
	plot.yaxis.major_label_text_font_size = "14pt"
	return(plot)



def generate_bar_plots(df, time_strings, color_dict, colors):

    plot1 = generate_single_bar(df[0], time_strings[0], color_dict, colors)
    plot2 = generate_single_bar(df[4], time_strings[4], color_dict, colors)
    plot3 = generate_single_bar(df[8], time_strings[8], color_dict, colors)

    tab1 = Panel(child=plot1, title=time_strings[0])
    tab2 = Panel(child=plot2, title=time_strings[4])
    tab3 = Panel(child=plot3, title=time_strings[8])
        
    tabs = Tabs(tabs=[tab1, tab2, tab3])
    layout = row(tabs)
    return layout


stand_alone_test = False
if stand_alone_test:
    import load_data
    from bokeh.io import show
    adf, time_strings, color_dict, colors = load_data.get_summary_data()
    dplt = generate_bar_plots(adf, time_strings,color_dict,colors)
    show(dplt)