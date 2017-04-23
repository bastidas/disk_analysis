from bokeh.charts import Bar, output_file, show
from bokeh.models import ColumnDataSource, Plot, Range1d
from bokeh.models.widgets import Panel, Tabs, DataTable, TableColumn
from bokeh.layouts import layout, row
from bokeh.plotting import figure
from bokeh.models import HoverTool
import numpy as np
from bokeh.models.glyphs import HBar


def generate_single_table(df, time_str, color_dict, colors):
	fill = [color_dict[model_key] if model_key in color_dict else 'grey' for model_key in df.model]
	data = dict(manufacturer = [m for m in df['manufacturer']],
				color=[c for c in df['color']],
				model=[m for m in df['model']],
				failure_rate=[np.round(f,2) for f in df['failure_rate']],
				count=[c for c in df['count']])
	source = ColumnDataSource(data)

	columns = [TableColumn(field="manufacturer", title="manufacturer"),
				TableColumn(field="model", title="model"),
				TableColumn(field="count", title="count"),
				TableColumn(field="failure_rate", title="failure rate")]
				   #TableColumn(field="model", title="model"),

	xdr = Range1d(start=0, end=20)
	ydr = Range1d(start=-2, end=2)
	title = 'Failure Rate'
	bar_fig = figure(title=title, x_range=xdr, y_range=ydr, width = 270, height = 570)


	table_plot = DataTable(source=source, columns=columns, width = 640, height = 700, row_headers=False, sortable=False)#, x_range=xdr, y_range=ydr)
	#table_plot.font.text_font_size = 14


	bar_data = dict(manufacturer = [m for m in df['manufacturer']],
				color=[c for c in df['color']],
				y=np.linspace(1.9,-1.8, len(df)),
				right=[np.round(f,2) for f in df['failure_rate']],
				count=[c for c in df['count']])
	bar_source = ColumnDataSource(bar_data)

	bar_plot = HBar(y='y', right='right', left=0, height=.14,fill_color='color', line_color='white')#, tools=['hover'], outline_line_color="color", border_fill_color='color', color='color', legend=None)

	#bar_plot.grid.grid_line_alpha = 0
	#bar_plot .ygrid.band_fill_color = None
	#bar_plot .ygrid.band_fill_alpha = 0.1
	#bar_plot.x_range.range_padding = 0
	bar_fig.add_glyph(bar_source,bar_plot)
	bar_fig.min_border_top = 0
	bar_fig.yaxis.visible = False
	#plot.xaxis.axis_line_width = 2
	#plot.yaxis.axis_line_width = 2
	bar_fig.title.text_font_size = '16pt'
	#plot.xaxis.axis_label_text_font_size = "14pt"
	#plot.xaxis.major_label_text_font_size = "14pt"
	#plot.yaxis.axis_label_text_font_size = "14pt"
	#plot.yaxis.major_label_text_font_size = "14pt"
	bar_fig.ygrid.grid_line_color = None
	bar_fig.xgrid.grid_line_color = None
	bar_fig.toolbar.logo = None
	bar_fig.outline_line_width = 0
	bar_fig.outline_line_color = "white"
	layout = row(table_plot, bar_fig)
	return layout
	#return(plot)

def generate_table_plots(df, time_strings, color_dict, colors):

    plot1 = generate_single_table(df[0], time_strings[0], color_dict, colors)
    plot2 = generate_single_table(df[4], time_strings[4], color_dict, colors)
    plot3 = generate_single_table(df[8], time_strings[8], color_dict, colors)

    tab1 = Panel(child=plot1, title=time_strings[0])
    tab2 = Panel(child=plot2, title=time_strings[4])
    tab3 = Panel(child=plot3, title=time_strings[8])
        
    tabs = Tabs(tabs=[tab1, tab2, tab3])
    layout = row(tabs)
    return layout


stand_alone_test = False
if stand_alone_test:
    print ('show')
    import load_data
    from bokeh.io import show
    adf, time_strings, color_dict, colors = load_data.get_summary_data()
    dplt = generate_table_plots(adf, time_strings, color_dict, colors)#seagate_color_dict, hitachi_color_dict, hgst_color_dict, western_color_dict)
    show(dplt)