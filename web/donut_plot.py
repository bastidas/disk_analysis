from math import pi, sin, cos
from bokeh.models.glyphs import Wedge, AnnularWedge, ImageURL, Text
from bokeh.models import ColumnDataSource, Plot, Range1d
import numpy as np
from bokeh.palettes import brewer
#import load_data
from bokeh.models.widgets import Panel, Tabs
#from bokeh.io import show
from bokeh.layouts import layout
from bokeh.layouts import row


def generate_single_pie(df, time_str, color_dict):
    ncolor = 9
    nextra = 20
    blues = brewer["Blues"][ncolor][0:ncolor-1]
    blues = blues + [blues[ncolor-2] for i in range(nextra)]
    greens = brewer["Greens"][ncolor][0:ncolor-1]
    greens = greens + [greens[ncolor-2] for i in range(nextra)]
    reds = brewer["Reds"][ncolor][0:ncolor-1]
    reds = reds + [reds[ncolor-2] for i in range(nextra)]
    greys = brewer["Greys"][ncolor][0:ncolor-2][::-1]
    greys = greys + [greys[ncolor-3] for i in range(nextra)]
    purples = brewer["Purples"][ncolor][0:ncolor-1]
    purples = purples + [purples[ncolor-2] for i in range(nextra)]
    colors = {"Hitachi": reds, "Seagate": blues, "HGST": greens, "Samsung": greys, "Western Digital" : purples, "Toshiba": greys, "Other": greys}
    
    xdr = Range1d(start=-2, end=2)
    ydr = Range1d(start=-2, end=2)

    title = "Distribution of Drives " + time_str
    plot = Plot(title=title, x_range=xdr, y_range=ydr, plot_width=600, plot_height=600)


    plot.outline_line_width = 0
    plot.outline_line_alpha = 0.0
    plot.outline_line_color = "black"
    plot.border_fill_color = "black"
    plot.background_fill_color = "black"
    plot.title.text_color = 'white'
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
        colors = [colors[browser][0] for browser in browsers ],
    ))

    glyph = Wedge(x=0, y=0, radius=1, line_color="black",
        line_width=1, start_angle="start", end_angle="end", fill_color="colors")
    plot.add_glyph(browsers_source, glyph)

    def polar_to_cartesian(r, start_angles, end_angles):
        cartesian = lambda r, alpha: (r*cos(alpha), r*sin(alpha))
        points = []

        for start, end in zip(start_angles, end_angles):
            points.append(cartesian(r, (end + start)/2))

        return zip(*points)

    first = True

    show_wedge_percent = .01
    show_label_percent = 1.5
    for manufac, start_angle, end_angle in zip(browsers, start_angles, end_angles):
        versions = df[(df.manufacturer == manufac) & (df.percent_total >= show_wedge_percent)] #if it has gt than 
        angles = versions.percent_total.map(radians).cumsum() + start_angle
        end = angles.tolist() + [end_angle]
        start = [start_angle] + end[:-1]
        base_color = colors[manufac]

        fill = [color_dict[model_key] if model_key in color_dict else 'grey' for model_key in versions.model]

        text = [ number if share >= show_label_percent else "" for number, share in zip(versions.model, versions.percent_total) ]
        x, y = polar_to_cartesian(1.25, start, end)

        source = ColumnDataSource(dict(start=start, end=end, fill=fill))
        glyph = AnnularWedge(x=0, y=0,
            inner_radius=1, outer_radius=1.5, start_angle="start", end_angle="end",
            line_color="black", line_width=0, fill_color="fill")
        plot.add_glyph(source, glyph)


        text_angle = [(start[i]+end[i])/2 for i in range(len(start))]
        text_angle = [angle + pi if pi/2 < angle < 3*pi/2 else angle for angle in text_angle]

        text_source = ColumnDataSource(dict(text=text, x=x, y=y, angle=text_angle))
        glyph = Text(x="x", y="y", text="text", angle="angle",
            text_align="center", text_baseline="middle", text_color = "white")
        plot.add_glyph(text_source, glyph)


    x, y = polar_to_cartesian(1.7, start_angles, end_angles)

    text = [ "%.02f%%" % value for value in selected.percent_total]
    x, y = polar_to_cartesian(0.7, start_angles, end_angles)

    text_source = ColumnDataSource(dict(text=text, x=x, y=y))
    glyph = Text(x="x", y="y", text="text", text_align="center", text_baseline="middle", text_color = "white")
    plot.add_glyph(text_source, glyph)
    return plot

def generate_pie_plots(df, time_strings, seagate_color_dict, hitachi_color_dict, hgst_color_dict, western_color_dict):
    ncolor = 9
    nextra = 20


    blues = brewer["Blues"][ncolor][0:ncolor-1]
    blues = blues + [blues[ncolor-2] for i in range(nextra)]
    greens = brewer["Greens"][ncolor][0:ncolor-1]
    greens = greens + [greens[ncolor-2] for i in range(nextra)]
    reds = brewer["Reds"][ncolor][0:ncolor-1]
    reds = reds + [reds[ncolor-2] for i in range(nextra)]
    greys = brewer["Greys"][ncolor][0:ncolor-2][::-1]
    greys = greys + [greys[ncolor-3] for i in range(nextra)]
    purples = brewer["Purples"][ncolor][0:ncolor-1]
    purples = purples + [purples[ncolor-2] for i in range(nextra)]
    seagate_colors = blues
    hgst_colors = greens
    hitachi_colors = reds
    western_colors = purples
    colors = {"Hitachi": reds, "Seagate": blues, "HGST": greens, "Samsung": greys, "Western Digital" : purples, "Toshiba": greys, "Other": greys}
    color_dict = dict(seagate_color_dict, **hitachi_color_dict)
    color_dict = dict(color_dict, **hgst_color_dict)
    color_dict = dict(color_dict, **western_color_dict)

    plot1 = generate_single_pie(df[0], time_strings[0], color_dict)
    plot2 = generate_single_pie(df[4], time_strings[4], color_dict)
    plot3 = generate_single_pie(df[8], time_strings[8], color_dict)

    tab1 = Panel(child=plot1, title=time_strings[0])
    tab2 = Panel(child=plot2, title=time_strings[4])
    tab3 = Panel(child=plot3, title=time_strings[8])
        
    tabs = Tabs(tabs=[tab1, tab2, tab3])
    layout = row(tabs)
    return layout



#adf, time_strings, seagate_color_dict, hitachi_color_dict, hgst_color_dict, western_color_dict = load_data.get_summary_data()
#print(len(adf))
#dplt = generate_pie_plots(adf, time_strings, seagate_color_dict, hitachi_color_dict, hgst_color_dict, western_color_dict)
#show(dplt)