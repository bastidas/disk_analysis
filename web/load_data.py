import pandas as pd
import numpy as np
from bokeh.palettes import brewer


def make_color_dict(model, color_dict, color_index, manufac_colors):
    if model not in color_dict.keys():
            color_index +=1
            #color_dict[model] = color_index
            color_dict[model] = manufac_colors[color_index]
    return color_dict, color_index


def get_summary_data():
    dfiles = ['2014_Q1.csv', '2014_Q2.csv', '2014_Q3.csv', '2014_Q4.csv',
    '2015_Q1.csv', '2015_Q2.csv' , '2015_Q3.csv', '2015_Q4.csv',
    '2016_Q1.csv', '2016_Q2.csv', '2016_Q3.csv', '2016_Q4.csv']

    seagate_color_dict = {}
    seagate_color_index = -1
    hitachi_color_dict = {}
    hitachi_color_index = -1
    hgst_color_dict = {}
    hgst_color_index = -1
    western_color_dict = {}
    western_color_index = -1

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

    adf = []
    for file in dfiles:
        df = pd.read_csv("data/" + file)
        df['percent_total'] = df['percent_total'] * 100.0  # convert decimal to percent
        df = df.loc[df['percent_total'] >=.01] 
        del df['Unnamed: 0']  # delete malformed index row
        #for cn in df.columns:
        #    df.rename(columns={cn: cn.replace("_", " ")}, inplace=True)  # clean up column names
        adf.append(df)
        sdf = df.sort_values(by="percent_total")
        sdf = sdf[sdf['percent_total'] >= .7]
        for model,manufac in zip(list(sdf.model),list(sdf.manufacturer)):
            if manufac == "Seagate":
                    seagate_color_dict, seagate_color_index = \
                    make_color_dict(model,seagate_color_dict, seagate_color_index, seagate_colors)
            if manufac == "Hitachi":
                    hitachi_color_dict, hitachi_color_index = \
                    make_color_dict(model,hitachi_color_dict, hitachi_color_index, hitachi_colors)
            if manufac == "HGST":
                    hgst_color_dict, hgst_color_index = \
                    make_color_dict(model,hgst_color_dict, hgst_color_index, hgst_colors)
            if manufac == "Western Digital":
                    western_color_dict, western_color_index = \
                    make_color_dict(model,western_color_dict, western_color_index, western_colors)
    time_strings = [x.replace(".csv", "").replace("_", " ") for x in dfiles]  # create clean time names 
    return adf, time_strings, seagate_color_dict, hitachi_color_dict, hgst_color_dict, western_color_dict