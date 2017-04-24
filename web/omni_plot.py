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
from bokeh.models.widgets import Select, Toggle, RadioButtonGroup, Button, Slider
from bokeh.layouts import row, widgetbox, column
from bokeh.models import LinearAxis

 

def generate_summary_plot(hds, hcols):
	"""
	hcols maps cols to human readable cols
	so for example hcol[col[n]] would be the name of an axis
	"""
	aux_cols = ['Model', "Number_of_Drives", "Percent_of_Drives", "Color"]
	cols = ['Failure_Rate', 'Capacity', 'Interface', 'Cache', 'RPM', 'Price_GB']

	x_start = 5
	y_start = 0

	data = {}
	for c in cols:
		#print('col: ', c)
		data[c] = hds[c]
	for c in aux_cols:
		#print('col: ', c)
		data[c] = hds[c]

	data["x"] = hds[cols[x_start]]
	data["y"] = hds[cols[y_start]]


	sizes = list(range(6, 24, 4))
	groups = pd.cut(hds["Capacity"].values, len(sizes))
	sz = [sizes[i] for i in groups.codes]
	data["Size"] = sz 

	_source = ColumnDataSource(data=data)

	hcols_data = {}
	for c in hcols.keys():
		hcols_data[c] = [hcols[c]]
	_hcols_source = ColumnDataSource(data=hcols_data)


	title = "Exploratory Plot of Hard Drives " #+ time_strings[n]
	plot = figure(title=title, x_axis_location='below', y_axis_location='left', tools=['hover,box_zoom,wheel_zoom,save,reset'])
	hover = plot.select(dict(type=HoverTool))
	hover.tooltips = [
		("Model ", "@Model"),
        ("Failure Rate ", "@Failure_Rate"),
        (hcols["Capacity"], "@Capacity"),
        (hcols["Interface"], "@Interface"),
        (hcols["RPM"], "@RPM"),
        (hcols["Cache"], "@Cache"),
        (hcols["Price_GB"], "@Price_GB{1.11}")
        ]

	p1 = plot.circle('x', 'y', source = _source, color='Color', size='Size')#, line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5)
	
	plot.toolbar.logo = None
	plot.xaxis.visible = False
	plot.yaxis.visible = False
	xaxis = LinearAxis(axis_label=hcols[cols[x_start]])
	yaxis = LinearAxis(axis_label=hcols[cols[y_start]])
	plot.add_layout(xaxis, 'below')
	plot.add_layout(yaxis, 'left')

	update_x = CustomJS(args=dict(source=_source, xaxis = xaxis, hcols = _hcols_source), code="""
	var hcols = hcols.get("data");
	var data = source.get("data");
	var f = cb_obj.value
	xaxis.attributes.axis_label = hcols[f][0]
	data['x'] = data[f]
	source.trigger('change');
	""")

	update_y = CustomJS(args=dict(source=_source, yaxis = yaxis, hcols = _hcols_source), code="""
	var hcols = hcols.get("data");
	var data = source.get("data");
	var f = cb_obj.value
	yaxis.attributes.axis_label = hcols[f][0]
	data['y'] = data[f]
	source.trigger('change');
	""")

	plot.min_border_left = 15
	plot.xaxis.axis_line_width = 2
	plot.yaxis.axis_line_width = 2
	plot.title.text_font_size = '16pt'
	plot.xaxis.axis_label_text_font_size = "14pt"
	plot.xaxis.major_label_text_font_size = "14pt"
	plot.yaxis.axis_label_text_font_size = "14pt"
	plot.yaxis.major_label_text_font_size = "14pt"
	plot.ygrid.grid_line_color = None
	plot.xgrid.grid_line_color = None
	plot.toolbar.logo = None
	plot.outline_line_width = 0
	plot.outline_line_color = "white"

	x_axis_select = Select(title='X-Axis', value=cols[x_start], options=cols)
	x_axis_select.js_on_change('value', update_x)
	y_axis_select = Select(title='Y-Axis', value=cols[y_start], options=cols)
	y_axis_select.js_on_change('value', update_y)
	controls = widgetbox([x_axis_select, y_axis_select], width=200)
	layout = row(controls, plot)
	return layout



def generate_omni_plot(adf, time_strings):#, colors):
	n = 6 
	df = adf[n]
	sizes = list(range(6, 36, 3))
	sz = 9
	groups = pd.cut(df['size'].values, len(sizes))
	sz = [sizes[i] for i in groups.codes]
	columns = ['size','failure_rate','count']

	data=dict(
	x = df[columns[0]],
	y = df[columns[1]],
	c = df['color'],
	s = sz,
	size = df['size'],
	model = df['model'],
	count = df['count'],
	failure_rate = df['failure_rate']
	)

	_source = ColumnDataSource(data=data)

	title = "Exploratory Plot of Hard Drives " + time_strings[n]
	plot = figure(title=title, x_axis_location='below', y_axis_location='left', tools=['hover,box_zoom,wheel_zoom,save,reset'])
	hover = plot.select(dict(type=HoverTool))
	hover.tooltips = [
		("Model ", "@model"),
        ("Failure Rate ", "@failure_rate")]

	p1 = plot.circle('x', 'y', source = _source, color='c', size='s')#, line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5)
	
	plot.toolbar.logo = None
	plot.xaxis.visible = False
	plot.yaxis.visible = False

	xaxis = LinearAxis(axis_label=cos[x_start])
	yaxis = LinearAxis(axis_label=cos[y_start])
	plot.add_layout(xaxis, 'below')
	plot.add_layout(yaxis, 'left')


	update_x = CustomJS(args=dict(source=_source, xaxis = xaxis), code="""
	var data = source.get("data");
	var f = cb_obj.value
	xaxis.attributes.axis_label = f
	data['x'] = data[f]
	source.trigger('change');
	""")

	update_y = CustomJS(args=dict(source=_source, yaxis = yaxis), code="""
	var data = source.get("data");
	var f = cb_obj.value
	yaxis.attributes.axis_label = f
	data['y'] = data[f]
	source.trigger('change');
	""")

	plot.min_border_left = 15
	plot.xaxis.axis_line_width = 2
	plot.yaxis.axis_line_width = 2
	plot.title.text_font_size = '16pt'
	plot.xaxis.axis_label_text_font_size = "14pt"
	plot.xaxis.major_label_text_font_size = "14pt"
	plot.yaxis.axis_label_text_font_size = "14pt"
	plot.yaxis.major_label_text_font_size = "14pt"
	plot.ygrid.grid_line_color = None
	plot.xgrid.grid_line_color = None
	plot.toolbar.logo = None
	plot.outline_line_width = 0
	plot.outline_line_color = "white"

	#var title = p.title
	#title.set({"text": f})
	#slider = Slider(start=0.1, end=4, value=1, step=.1, title="power")
	#slider.js_on_change('value', callback)
	#time_strings = [x.replace(".csv", "").replace("_", " ") for x in dfiles]  # create clean time names
	#time_indexer = dict(zip(time_strings, range(len(time_strings))))

	x_axis_select = Select(title='X-Axis', value=columns[0], options=columns)
	x_axis_select.js_on_change('value', update_x)
	y_axis_select = Select(title='Y-Axis', value=columns[1], options=columns)
	y_axis_select.js_on_change('value', update_y)
	controls = widgetbox([x_axis_select, y_axis_select], width=200)
	layout = row(controls, plot)
	return layout


def generate_box_plot(sdf, colors):
	"""
	The colors were hacked in here!
	If the columns are not as in the order below in the final output, the colors will be wrong!
	"""
	from bokeh.charts import BoxPlot
	from bokeh.charts import color
	box_colors = [colors["HGST"], colors["Hitachi"], colors["Seagate"], colors["Toshiba"], colors["Western Digital"]]
	#palette = box_colors
	#print(box_colors)
	plot = BoxPlot(sdf, values='failure_rate', label='manufacturer',
            title="Failure Rate by Manufacturer", outliers=False, 
            color=color(columns=['manufacturer'], palette=box_colors), legend=False, tools=None)

	plot.yaxis.axis_label = "Failure Rate"
	plot.xaxis.axis_line_width = 2
	plot.yaxis.axis_line_width = 2
	plot.title.text_font_size = '16pt'
	plot.xaxis.axis_label_text_font_size = "14pt"
	plot.xaxis.major_label_text_font_size = "14pt"
	plot.yaxis.axis_label_text_font_size = "14pt"
	plot.yaxis.major_label_text_font_size = "14pt"
	plot.y_range = Range1d(0, 15)
	plot.ygrid.grid_line_color = None
	plot.toolbar.logo = None
	plot.outline_line_width = 0
	plot.outline_line_color = "white"
	return plot


def generate_choose_plot(hds, color_dict, hcols):
	#print(c1.columns)
	aux_cols = ['Model', "Number_of_Drives", "Percent_of_Drives", "Color"]
	cols = ['Failure_Rate', 'Capacity', 'Interface', 'Cache', 'RPM', 'Price_GB']

	data = {}
	for c in cols:
		#print('col: ', c)
		data[c] = hds[c]
	for c in aux_cols:
		#print('col: ', c)
		data[c] = hds[c]

	init_x = 0
	init_y = 1
	data["x"] = hds[cols[0]]
	data["y"] = hds[cols[1]]

	sizes = list(range(6, 24, 4))
	groups = pd.cut(hds["Capacity"].values, len(sizes))
	sz = [sizes[i] for i in groups.codes]
	data["Size"] = sz


	_source = ColumnDataSource(data=data)

	title = "What Matters in a Hard Drive?" 
	plot = figure(title=title, x_axis_location='below', y_axis_location='left', tools=['hover,box_zoom,wheel_zoom,save,reset'])
	hover = plot.select(dict(type=HoverTool))
	hover.tooltips = [
		("Model ", "@Model"),
        ("Failure Rate ", "@Failure_Rate"),
        (hcols["Capacity"], "@Capacity"),
        (hcols["Interface"], "@Interface"),
        (hcols["RPM"], "@RPM"),
        (hcols["Cache"], "@Cache"),
        (hcols["Price_GB"], "@Price_GB{1.11}")
        ]

	p1 = plot.circle('x', 'y', source = _source, size='Size', color="Color")#, line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5)
	
	plot.toolbar.logo = None
	plot.xaxis.visible = False
	plot.yaxis.visible = False

	xaxis = LinearAxis(axis_label=hcols[cols[init_x]])
	yaxis = LinearAxis(axis_label=hcols[cols[init_y]])
	plot.add_layout(xaxis, 'below')
	plot.add_layout(yaxis, 'left')


	#hcols = ColumnDataSource(data=hcols)
	update_x = CustomJS(args=dict(source=_source, xaxis=xaxis), code="""
	var data = source.get("data");
	var f = cb_obj.value
	xaxis.attributes.axis_label = f
	data['x'] = data[f]
	source.trigger('change');
	""")

	update_y = CustomJS(args=dict(source=_source, yaxis = yaxis), code="""
	var data = source.get("data");
	var f = cb_obj.value
	yaxis.attributes.axis_label = f
	data['y'] = data[f]
	source.trigger('change');
	""")

	plot.xaxis.axis_line_width = 2
	plot.yaxis.axis_line_width = 2
	plot.title.text_font_size = '16pt'
	plot.xaxis.axis_label_text_font_size = "14pt"
	plot.xaxis.major_label_text_font_size = "14pt"
	plot.yaxis.axis_label_text_font_size = "14pt"
	plot.yaxis.major_label_text_font_size = "14pt"
	plot.ygrid.grid_line_color = None
	plot.xgrid.grid_line_color = None
	plot.toolbar.logo = None
	plot.outline_line_width = 0
	plot.outline_line_color = "white"
	plot.plot_height = 900
	plot.plot_width = 900
	x_axis_select = Select(title='X-Axis', value=cols[init_x], options=cols)
	x_axis_select.js_on_change('value', update_x)
	y_axis_select = Select(title='Y-Axis', value=cols[init_y], options=cols)
	y_axis_select.js_on_change('value', update_y)
	controls = widgetbox([x_axis_select, y_axis_select], width=200)
	layout = row(controls, plot)
	return layout

def generate_performance_plot(hds, hcols):
	aux_cols = ['Model', "Number_of_Drives", "Percent_of_Drives", "Color"]
	cols = ['Failure_Rate', 'Capacity', 'Interface', 'Cache', 'RPM', 'Price_GB']

	data = {}
	for c in cols:
		#print('col: ', c)
		data[c] = hds[c]
	for c in aux_cols:
		#print('col: ', c)
		data[c] = hds[c]

	max_scale = 1.0
	min_scale = 0.0

	max_cache = np.max(hds["Cache"])
	min_cache = np.min(hds["Cache"])
	cache = ( (max_scale - min_scale) /(max_cache - min_cache))*(hds["Cache"] - max_cache) + max_scale
	max_rpm = np.max(hds["RPM"])
	min_rpm = np.min(hds["RPM"])
	rpm = ( (max_scale - min_scale) /(max_rpm - min_rpm))*(hds["RPM"] - max_rpm) + max_scale
	max_interface = np.max(hds["Interface"])
	min_interface = np.min(hds["Interface"])
	interface = ( (max_scale - min_scale) /(max_interface - min_interface))*(hds["Interface"] - max_interface) + max_scale
	performance = interface + rpm + cache
	max_performance = np.max(performance)
	min_performance = np.min(performance)
	performance = ( (max_scale - min_scale) /(max_performance - min_performance))*(performance - max_performance) + max_scale
	max_failure = np.max(hds["Failure_Rate"])
	min_failure = np.min(hds["Failure_Rate"])
	reliability = ( (max_scale - min_scale) /(max_failure - min_failure))*(hds["Failure_Rate"] - max_failure) + max_scale
	reliability = 1.0 - reliability

	max_cost = np.max(hds["Price_GB"])
	min_cost = np.min(hds["Price_GB"])
	cost = ( (max_scale - min_scale) /(max_cost-min_cost))*(hds["Price_GB"]-max_cost) + max_scale
	cost = 1.0 - cost

	slider_start = .5
	data["x"] = np.arange(0,len(hds['Model']),1)
	data["y"] = slider_start * cost + slider_start * performance + slider_start * reliability
	data["Cost"] = slider_start * cost
	data["Performance"] = slider_start * performance
	data["Reliability"] = slider_start * reliability
	sizes = list(range(6, 24, 4))
	groups = pd.cut(hds["Capacity"].values, len(sizes))
	sz = [sizes[i] for i in groups.codes]
	data["Size"] = sz

	static_data = {}
	static_data["Cost"] = cost
	static_data["Performance"] = performance
	static_data["Reliability"] = reliability

	_source = ColumnDataSource(data=data)
	_static_source = ColumnDataSource(data=static_data)

	title = "Relative Hard Drive Value" 
	plot = figure(title=title, x_axis_location='below', y_axis_location='left', tools=['hover','save'])
	hover = plot.select(dict(type=HoverTool))
	hover.tooltips = [
		("Model ", "@Model"),
        ("Failure Rate ", "@Failure_Rate"),
        (hcols["Capacity"], "@Capacity"),
        (hcols["Interface"], "@Interface"),
        (hcols["RPM"], "@RPM"),
        (hcols["Cache"], "@Cache"),
        (hcols["Price_GB"], "@Price_GB{1.11}")
        ]

	p1 = plot.circle('x', 'y', source = _source, size='Size', color="Color")#, line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5)
	
	from bokeh.models import FuncTickFormatter#, FixedTickFormatter
	label_dict = {}
	for i, s in enumerate(hds["Model"]):
		label_dict[i] = s
	
	plot.y_range = Range1d(-.1, 3.1)
	plot.toolbar.logo = None
	
	plot.xaxis.visible = False
	plot.yaxis.visible = False
	from bokeh.models import SingleIntervalTicker
	ticker = SingleIntervalTicker(interval=1, num_minor_ticks=0)
	xaxis = LinearAxis(axis_label="Model", ticker=ticker)
	#yaxis = LinearAxis()#axis_label="Relative Merit")

	xaxis.formatter = FuncTickFormatter(code="""
    var labels = %s;
    return labels[tick];
	""" % label_dict)

	xaxis.major_label_orientation = -np.pi/2.7

	plot.add_layout(xaxis, 'below')
	#plot.add_layout(yaxis, 'left')

	callback1 = CustomJS(args=dict(source=_source, static_source=_static_source), code="""
	var data = source.get("data");
	var static_data = static_source.get("data");
	var f = cb_obj.value
	y = data['y']
	reli = data['Reliability']
	perf = data['Performance']
	cost = data['Cost']
	static_cost = static_data['Cost']
	for (i = 0; i < y.length; i++) {
		cost[i] = f * static_cost[i]
        y[i] = reli[i] + cost[i] + perf[i]
    }
	source.trigger('change');
	""")

	callback2 = CustomJS(args=dict(source=_source, static_source=_static_source), code="""
	var data = source.get("data");
	var static_data = static_source.get("data");
	var f = cb_obj.value
	y = data['y']
	reli = data['Reliability']
	static_reli = static_data['Reliability']
	perf = data['Performance']
	cost = data['Cost']
	for (i = 0; i < y.length; i++) {
		reli[i] = f * static_reli[i]
        y[i] = reli[i] + cost[i] + perf[i]
    }
	source.trigger('change');
	""")

	callback3 = CustomJS(args=dict(source=_source, static_source=_static_source), code="""
	var data = source.get("data");
	static_data = static_source.get("data");
	var f = cb_obj.value
	y = data['y']
	reli = data['Reliability']
	perf = data['Performance']
	static_perf = static_data['Performance']
	cost = data['Cost']
	for (i = 0; i < y.length; i++) {
		perf[i] = f*static_perf[i]
        y[i] = reli[i] + cost[i] + perf[i]
    }
	source.trigger('change');
	""")

	plot.min_border_left = 0
	plot.xaxis.axis_line_width = 2
	plot.yaxis.axis_line_width = 2
	plot.title.text_font_size = '16pt'
	plot.xaxis.axis_label_text_font_size = "14pt"
	plot.xaxis.major_label_text_font_size = "14pt"
	plot.yaxis.axis_label_text_font_size = "14pt"
	plot.yaxis.major_label_text_font_size = "14pt"
	plot.ygrid.grid_line_color = None
	plot.xgrid.grid_line_color = None
	plot.toolbar.logo = None
	plot.outline_line_width = 0
	plot.outline_line_color = "white"

	slider1 = Slider(start=0.0, end=1.0, value=slider_start, step=.05, title="Price")
	slider2 = Slider(start=0.0, end=1.0, value=slider_start, step=.05, title="Reliability")
	slider3 = Slider(start=0.0, end=1.0, value=slider_start, step=.05, title="Performance")
	slider1.js_on_change('value', callback1)
	slider2.js_on_change('value', callback2)
	slider3.js_on_change('value', callback3)
	controls = widgetbox([slider1, slider2,slider3], width=200)
	layout = row(controls, plot)
	return layout


def gather_stat_data(adf, color_dict):
	sdf = pd.DataFrame()
	for df in adf:
		df = df[df['count'] > 100 ]
		sdf = sdf.append(df, ignore_index=True)
	
	#summary_df = pd.concat(adf, ignore_index=True)

	aggregations = {
    'size': {
     'Capacity_in_TB': 'median'
    },
    'percent_total':{
        'Percent_of_Drives': 'max'
    },
    'count':{
        'Number_of_Drives': 'max'
    },
    'failures': { 
        'Total number of Failures': 'sum'
    },
    'failure_rate': { # smart 9 is the disk uptime
        'Failure_Rate': 'mean',  
        'Worst Failure Rate' : 'max',
        'Best Failure Rate' : 'min'  
    	}    
	}

	by_model = sdf.groupby(['model']).agg(aggregations).reset_index()
	by_model.columns = by_model.columns.droplevel()
	by_model.rename(columns={'': 'Model'}, inplace=True)

	#by_model2 = summary_df.groupby(['model']).agg(aggregations).reset_index()
	#by_model2.columns = by_model2.columns.droplevel()
	#by_model2.rename(columns={'': 'Model'}, inplace=True)

	specs = pd.read_csv("data/drive_stats.csv")
	del specs['Unnamed: 0']
	del specs['Manufacturer'] 
	del specs['Form Factor']
	specs.rename(columns={'Price/GB': 'Price_GB'}, inplace=True)
	specs.rename(columns={'Part #': 'Part'}, inplace=True)
	specs["Price_GB"] = specs["Price_GB"].map(lambda x: np.round(float(x.lstrip("$")),2))
	specs["Cache"] = specs["Cache"].map(lambda x: float(x.strip("MB")))
	specs["Capacity"] = specs["Capacity"].map(lambda x: float(x.strip("TB")) if "TB" in x else float(x.strip("GB"))/1000.0)
	specs["Interface"] = specs["Interface"].map(lambda x: float(x.lstrip("SATA").rstrip("Gb/s")))
	hcols = {}
	hcols["Cache"] = "Cache in MB"
	hcols["RPM"] = "Platter Speed in RPM"
	hcols["Capacity"] = "Capacity in TB"
	hcols["Price_GB"] = "Price in $ per GB"
	hcols["Interface"] = "SATA Interface speed in Gb/s"
	hcols["Failure_Rate"] = "Average Annual Naive Failure Rate Percent"
	hcols["Model"] = "Model Number"

	color = [str(color_dict[model_key]) if model_key in color_dict else 'grey' for model_key in specs["Part"]]
	specs["Color"] = color
	#print(specs.columns)
	c1 = pd.merge(by_model, specs, how='inner', left_on="Model", right_on="Part")
	#c2 = pd.merge(by_model2, specs, how='inner', left_on="Model", right_on="Part")
	return c1, sdf, hcols


stand_alone_test = False
if stand_alone_test:
	import load_data
	from bokeh.io import show
	adf, time_strings, color_dict, colors = load_data.get_summary_data()
	c1, sdf, hcols = gather_stat_data(adf, color_dict)
	#dplt = generate_box_plot(sdf, colors)
	#print(sdf)
	#print(adf[0])
	#dplt = generate_omni_plot(adf,time_strings)
	dplt = generate_summary_plot(c1, hcols)
	#dplt = generate_performance_plot(c1, hcols)
	show(dplt)