import pandas as pd
from bokeh.themes import Theme
from bokeh.layouts import row, widgetbox
from bokeh.models import Select, Label
from bokeh.palettes import Spectral5
from bokeh.plotting import curdoc, figure

dfiles = ['2014_Q1.csv', '2014_Q2.csv', '2014_Q3.csv', '2014_Q4.csv',
    '2015_Q1.csv', '2015_Q2.csv' , '2015_Q3.csv', '2015_Q4.csv',
    '2016_Q1.csv', '2016_Q2.csv', '2016_Q3.csv', '2016_Q4.csv']

adf = []
for file in dfiles:
    df = pd.read_csv("data/" + file)
    df['percent_total'] = df['percent_total'] * 100.0  # convert decimal to percent
    df = df.loc[df['failure_rate'] <=100]  # remove unreasonable failure rates
    df = df.loc[df['count'] >=100] # remove low statistic models
    del df['Unnamed: 0']  # delete malformed index row
    for cn in df.columns:
            df.rename(columns={cn: cn.replace("_", " ")}, inplace=True)  # clean up column names
    adf.append(df)


time_strings = [x.replace(".csv", "").replace("_", " ") for x in dfiles]  # create clean time names
time_indexer = dict(zip(time_strings, range(len(time_strings))))

SIZES = list(range(6, 32, 3))
COLORS = Spectral5

columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]
quantileable = [x for x in continuous if len(df[x].unique()) > 11]


def create_figure():

    df = adf[time_indexer[t_index.value]]

    xs = df[x.value].values
    ys = df[y.value].values
    x_title = x.value.title()
    y_title = y.value.title()

    kw = dict()
    if x.value in discrete:
        kw['x_range'] = sorted(set(xs))
    if y.value in discrete:
        kw['y_range'] = sorted(set(ys))
    kw['title'] = "%s: %s vs %s" % (t_index.value, x_title, y_title)

    p = figure(plot_height=750, plot_width=750, tools='pan,box_zoom,reset', **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title
    p.toolbar.logo = None
    p.toolbar_location = None

    #label = Label(x=1.1, y=18, text=t_index.value, text_font_size='20pt', text_color='#eeeeee')
    #p.add_layout(label)

    if x.value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4

    sz = 9
    if size.value != 'None':
        #groups = pd.qcut(df[size.value].values, len(SIZES))
        groups = pd.cut(df[size.value].values, len(SIZES))
        sz = [SIZES[xx] for xx in groups.codes]

    c = "#31AADE"
    if color.value != 'None':
        #groups = pd.qcut(df[color.value].values, len(COLORS))
        groups = pd.cut(df[color.value].values, len(COLORS))
        c = [COLORS[xx] for xx in groups.codes]
    p.circle(x=xs, y=ys, color=c, size=sz, line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5)

    return p


def update(attr, old, new):
    layout.children[1] = create_figure()

t_index = Select(title='Year', value=time_strings[0], options=time_strings)
t_index.on_change('value', update)


x = Select(title='X-Axis', value='model', options=columns)
x.on_change('value', update)

y = Select(title='Y-Axis', value='failure rate', options=columns)
y.on_change('value', update)

size = Select(title='Size', value='None', options=['None'] + quantileable)
size.on_change('value', update)

color = Select(title='Color', value='None', options=['None'] + quantileable)
color.on_change('value', update)

controls = widgetbox([t_index, x, y, color, size], width=200)
layout = row(controls, create_figure())

curdoc().add_root(layout)
curdoc().title = "HD Data"
curdoc().theme = Theme(json={'attrs': {
    'Figure':{
        'background_fill_color': '#2F2F2F',
        'border_fill_color': '#FFFFFF',
        'outline_line_color': '#444444'},
    'Axis':{
        'axis_line_color': "white",
        'axis_label_text_color': '#2F2F2F',
        'major_label_text_color': '#2F2F2F',
        'major_tick_line_color': '#2F2F2F',
        'minor_tick_line_color': '#2F2F2F',
        'minor_tick_line_color': '#2F2F2F'},
    'Grid':{
        'grid_line_dash': [6, 4],
        'grid_line_alpha': .05},
    'Title':{
        'text_color': '#2F2F2F'}
    }})
