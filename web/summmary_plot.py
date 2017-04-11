import os
import numpy as np
import pandas as pd
from bokeh.plotting import ColumnDataSource
#from bokeh.models import HoverTool
from bokeh.io import push_notebook, show, output_notebook
from bokeh.models.widgets import Select, Toggle, RadioButtonGroup
#from bokeh.layouts import row
from bokeh.plotting import figure
#from bokeh.models import Range1d
#output_notebook()
#from bokeh.plotting import figure
#from bokeh.embed import 
from bokeh.layouts import row, widgetbox
from bokeh.models.callbacks import CustomJS
from bokeh.models import LinearAxis


def generate_summary_plot():
#x = [x*0.005 for x in range(0, 200)]
    #y = x
    x = np.arange(0, 10)
    #x = [x*0.005 for x in range(0, 200)]
    y = [i*i for i in x]

    z = [i*3.0 for i in x]

    source = ColumnDataSource(data=dict(x=x, y=y))
    source2 = ColumnDataSource(data=dict(x=x, z=z))

    print(source)
    print(dict(source=source))



    summary_fig = figure(x_axis_location='above', plot_width=400, plot_height=400)
    line_one = summary_fig.line('x', 'y', source=source, line_width=3, line_alpha=0.6)#, xaxis.axis_label = 'initalized')#,axis.axis_label='title')

    line_two = summary_fig.line('x', 'z', source=source2, line_width=3, line_alpha=0.6)#, xaxis.axis_label = 'initalized')#,axis.axis_label='title')

    #selector_options=['alpha','beta','gamma']
    #selector1=Select(title='X-Axis',value=selector_options[0],options=selector_options, callback = callback)
    
    #summary_fig.xaxis.visible = None
    xaxis = LinearAxis(axis_label="Initial x-axis label")
    summary_fig.add_layout(xaxis, 'below')
    #summary_fig.xaxis.axis_label = 'Time (Years)'    
    #selector1.on_change('value',callback)  #plot.yaxis.axis_label = y_title
    #controls = widgetbox([selector1], width=200)

    code1 = '''\
    object.visible = toggle.active
    '''

    code2 = '''\
    object.visible = radio_button.active
    '''

	#var f = cb_obj.value
    callback2 = CustomJS(args=dict(source=source2), code="""
    var data = source.data;
    var f = cb_obj.value
    x = data['x']
    z = data['z']
    if (f == "alpha") {
    	for (i = 0; i < x.length; i++) {
        z[i] = Math.pow(x[i], 3.)}
    	}
    else if (f = "beta") {
   		for (i = 0; i < x.length; i++) {
        z[i] = 20}
     	}
    source.trigger('change');
    """)


    callback3 = CustomJS(args=dict(xaxis=xaxis), code="""
    var f = cb_obj.value
    xaxis.attributes.axis_label = f 
    xaxis.trigger('change');
    """)


    callback4 = CustomJS(args=dict(source=source2), code="""
    var data = source.data;
    var f = cb_obj.value
    x = data['x']
    z = data['z']
    if (f == "A alpha") {
    	for (i = 0; i < x.length; i++) {
        z[i] = Math.pow(x[i], 3.)}
    	}
    else if (f = "B alpha") {
   		for (i = 0; i < x.length; i++) {
        z[i] = 20}
     	}
    source.trigger('change');
    """)



    callback1 = CustomJS.from_coffeescript(code=code1, args={})
    toggle1 = Toggle(label="Green Box", button_type="success", callback=callback1)
    callback1.args = {'toggle': toggle1, 'object': line_one}


    #callback2 = CustomJS.from_coffeescript(code=code2, args={})
    radio_button_group = RadioButtonGroup(labels=['alpha','beta','gamma'], active=0)# callback=callback2)
    radio_button_group.js_on_change('value', callback2)
    #print([method for method in dir(radio_button_group)])
    #callback2.args = {'radio_button': radio_button_group, 'object': line_two}
    #output_file("styling_visible_annotation_with_interaction.html")

    selector_options = ['A alpha', 'B beta', 'G gamma']
    selector1 = Select(title='X-Axis', value=selector_options[0], options=selector_options)#, callback=callback4)
    selector1.js_on_change('value', callback4)


    selector2_options = ['Aa alpha', 'Ba beta', 'Ga gamma']
    selector2 = Select(title='X-Axis', value=selector_options[0], options=selector2_options)#, callback=callback4)
    selector2.js_on_change('value', callback3)

    #slider = Slider(start=0.1, end=4, value=1, step=.1, title="power")
    #slider.js_on_change('value', callback)



    controls = widgetbox([toggle1,radio_button_group, selector1, selector2], width=200)
    layout = row(controls, summary_fig)
    return layout
#def update(attr, old, new):
#    layout.children[1] = generate_summary_plot()
#    print(selector1.value)
#    print(selector1.value.title())

#selector_options = ['alpha', 'beta', 'gamma']
#selector1 = Select(title='X-Axis', value=selector_options[0], options=selector_options)
#selector2 = Select(title='X-Axis', value=selector_options[0], options=selector_options)

#selector1.on_change('value', update)
#controls = widgetbox([selector1], width=200)
#layout = row(controls, generate_summary_plot())

agg = generate_summary_plot()
show(agg)
#show(layout)