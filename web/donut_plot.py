from math import pi, sin, cos
from bokeh.models.glyphs import Wedge, AnnularWedge, ImageURL, Text
from bokeh.models import ColumnDataSource, Plot, Range1d
import numpy as np
from bokeh.palettes import brewer
from bokeh.models.widgets import Panel, Tabs

from bokeh.layouts import layout, row
from bokeh.models import  LabelSet
from bokeh.plotting import figure
from bokeh.models import HoverTool

def generate_single_pie(df, time_str, color_dict, colors):

    xdr = Range1d(start=-2, end=2)
    ydr = Range1d(start=-2, end=2)
    xoffset = .45
    title = "Percent of Drive Models in use" + time_str
    #plot = Plot(title=title, x_range=xdr, y_range=ydr, plot_width=700, plot_height=600,tools=['hover'])
    
    plot = figure(title=title, x_range=xdr, y_range=ydr, plot_width=700, plot_height=600, tools=['hover,wheel_zoom,save'])
    hover = plot.select(dict(type=HoverTool))
    # = plot.select(dict(type=HoverTool))
    hover.tooltips = [
        ("Model ", "@model"),
        ("Failure Rate ", "@failure_rate")]
    hover.mode = 'mouse'

    plot.xaxis.visible = False
    plot.yaxis.visible = False
    plot.grid.grid_line_alpha = 0
    #plot.outline = None
    plot.outline_line_width = 0
    plot.ygrid.grid_line_color = None
    plot.toolbar.logo = None
    plot.outline_line_width = 0
    plot.outline_line_color = "white"
    aggregated = df.groupby("manufacturer").agg(sum)
    selected = aggregated[aggregated.percent_total >= 2].copy()
    selected.loc["Other"] = aggregated[aggregated.percent_total < 2].sum()
    browsers = selected.index.tolist()
    radians = lambda x: 2*pi*(x/100)
    angles = selected.percent_total.map(radians).cumsum()
    end_angles = angles.tolist()
    start_angles = [0] + end_angles[:-1]

    browsers_source = ColumnDataSource(dict(
        start  = start_angles,
        end    = end_angles,
        colors = [colors[browser] for browser in browsers],
        model = browsers,
        failure_rate = [f for f in selected["failure_rate"]]
    ))

    glyph = Wedge(x=xoffset, y=0, radius=.8, line_color="white",
        line_width=2, start_angle="start", end_angle="end", fill_color="colors")
    plot.add_glyph(browsers_source, glyph)

    def polar_to_cartesian(r, start_angles, end_angles):
        cartesian = lambda r, alpha: (r*cos(alpha), r*sin(alpha))
        points = []

        for start, end in zip(start_angles, end_angles):
            points.append(cartesian(r, (end + start)/2))

        return zip(*points)
    show_wedge_percent =  1.0
    show_label_percent = 1.0
    n = 0
    for manufac, start_angle, end_angle in zip(browsers, start_angles, end_angles):
        manufac_models = df[(df.manufacturer == manufac) & (df.percent_total > show_wedge_percent)] #if it has gt than 
        other_manufac_models = df[(df.manufacturer == manufac) & (df.percent_total <= show_wedge_percent)]
        other_manufac_models.model = "Other"
        manufac_models = manufac_models.append(other_manufac_models)
        manufac_models = manufac_models.reset_index().groupby("model").sum()
        manufac_models["model"] = manufac_models.index
        manufac_models = manufac_models[manufac_models.percent_total > show_wedge_percent] #if it has gt than 
        angles = manufac_models.percent_total.map(radians).cumsum() + start_angle
        end = angles.tolist() + [end_angle]
        start = [start_angle] + end[:-1]
        base_color = colors[manufac]
        fill = [color_dict[model_key] if model_key in color_dict else 'grey' for model_key in manufac_models.model]
        text = [ modnumber if share >= show_label_percent else " " for modnumber, share in zip(manufac_models.model, manufac_models.percent_total) ]
        x = np.zeros(len(manufac_models))-1.93
        y = [1.7 -.23*h-.23*n for h in range(len(manufac_models))]
        n += len(manufac_models)
        source = ColumnDataSource(dict(start=start, end=end, fill=fill,model=text, failure_rate= manufac_models.failure_rate))
        glyph = AnnularWedge(x= xoffset, y=0,
            inner_radius=.8, outer_radius=1.4, start_angle="start", end_angle="end",
            line_color="white", line_width=2, fill_color="fill")
        plot.add_glyph(source, glyph)



        text_source = ColumnDataSource(dict(text=text, x=x, y=y, fill=fill))
        labels = LabelSet(x='x', y='y', text='text', text_color= "white", level='glyph', source=text_source, \
            render_mode='canvas', background_fill_color="fill", border_line_color="fill", border_line_width=8)
        plot.add_layout(labels)
    x, y = polar_to_cartesian(1.7, start_angles, end_angles)



    selected = selected[selected['percent_total'] > 3.5]
    text = [ "%.02f%%" % value for value in selected.percent_total]
    x, y = polar_to_cartesian(0.6, start_angles, end_angles)
    x =  [i + xoffset-.02 for i in x]
    text_source = ColumnDataSource(dict(text=text, x=x, y=y))
    glyph = Text(x="x", y="y", text="text", text_align="center", text_baseline="middle", text_color = "white")
    plot.add_glyph(text_source, glyph)
    return plot

def generate_pie_plots(df, time_strings, color_dict, colors):

    plot1 = generate_single_pie(df[0], time_strings[0], color_dict, colors)
    plot2 = generate_single_pie(df[4], time_strings[4], color_dict, colors)
    plot3 = generate_single_pie(df[8], time_strings[8], color_dict, colors)

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
    dplt = generate_pie_plots(adf, time_strings, color_dict, colors)
    show(dplt)