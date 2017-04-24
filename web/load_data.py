import pandas as pd
import numpy as np
from bokeh.palettes import brewer


def get_summary_data():
    dfiles = ['2014_Q1.csv', '2014_Q2.csv', '2014_Q3.csv', '2014_Q4.csv',
    '2015_Q1.csv', '2015_Q2.csv' , '2015_Q3.csv', '2015_Q4.csv',
    '2016_Q1.csv', '2016_Q2.csv', '2016_Q3.csv', '2016_Q4.csv']

    ct =        ["#1f77b4", #blue           0
                "#aec7e8", #light_blue    1
                "#17becf", #blue2          2
                "#9edae5", #light_blue2   3
                "#98df8a", #light_green       4
                "#d62728", #red             5
                "#ff7f0e", #oragne          6
                "#ffbb78", #peach       7
                "#bcbd22", #yellow         8
                "#dbdb8d", #beige           9
                "#9467bd", #Purples       10
                "#ff9896", #pink            
                "#e377c2", #soft_pink    
                "#f7b6d2", #very_soft_pink     13       
                "#c5b0d5", #lavender
                "#2ca02c", #green
                "#8c564b", #brown
                "#c49c94", #bland           
                "#7f7f7f", #dark_grey
                "#c7c7c7"] #grey
                          
    grey = "#c7c7c7"

    seagate_colors = ct[0:5]
    hgst_colors = ct[5:10]
    hitachi_colors = ct[10:15]
    western_colors = ct[15:20]
    adf = []
    for file in dfiles:
        df = pd.read_csv("data/" + file)
        while len(df) > 20:
            min_model = df['count'].idxmin()
            df  =  df.drop(min_model)

        df['percent_total'] = 100.0 * df['count']/df['count'].sum()

        del df['Unnamed: 0']  # delete malformed index row
        adf.append(df)

    #2016 q1 as color reference
    ref = adf[8].sort_values(by="percent_total", ascending=False)
    color_dict= {}
    c1, c2, c3, c4 = 0, 0, 0, 0
    for model,manufac,percent_total in zip(list(ref.model),list(ref.manufacturer),list(ref.percent_total)):
            if manufac == "Seagate":
                if c1 < 5:
                    color_dict[model] = seagate_colors[c1]
                    c1 +=1 
            if manufac == "Hitachi":
                if c2 < 5:
                    color_dict[model] = hitachi_colors[c2]
                    c2 +=1 
            if manufac == "HGST":
                if c3 < 5:
                    color_dict[model] = hgst_colors[c3]
                    c3 +=1 
            if manufac == "Western Digital":
                if c4 < 5:
                    color_dict[model] = western_colors[c4]
                    c4 +=1 

    manufac_colors = {"Hitachi": hitachi_colors[0],
            "Seagate": seagate_colors[0],
            "HGST": hgst_colors[0],
            "Samsung": grey,
            "Western Digital" : western_colors[0],
            "Toshiba": grey, 
            "Other": grey} 

    for i in range(len(adf)):
        color = [str(color_dict[model_key]) if model_key in color_dict else 'grey' for model_key in adf[i].model]
        adf[i]["color"] = color


    time_strings = [x.replace(".csv", "").replace("_", " ") for x in dfiles]  # create clean time names 
    
    return adf, time_strings, color_dict, manufac_colors

def write_css_colors(color_dict):
    """
    Write colors really only needs to be run once after any color palette change
    The colors should come from color dict, but using a hack right now from hardcoded colors from km_plot.py
    """
    hack = True
    f = open("static/css/widget_style.css", "w")
    n = 0
    if not hack:
        for c in color_dict.values():
            new_style = ".bk-root .bk-" +  c.lstrip("#")  + "{\nbackground: " + c + " !important;\nborder: " + c + " !important; }"
            f.write(new_style)
            f.write("\n\n")

    if hack:
        km_colors = ['#1a1334', '#03c383', '#fbbf45', '#ed0345' ,  '#26294a', '#aad962', '#01545a', '#ef6a32','#017351','#a12a5e', '#710162', '#110141']
        for c in km_colors:
            new_style = ".bk-root .bk-" +  c.lstrip("#")  + "{\nbackground: " + c + " !important;\nborder: " + c + " !important; }"
            f.write(new_style)
            f.write("\n\n")

    new_style = ".bk-root .bk-" +  "grey"  + "{\nbackground: " + "grey" + " !important;\nborder: " + "grey" + " !important; }"    
    f.write(new_style)
    f.close()
    return None        


write_css = False
if write_css:
    adf, time_strings, color_dict, manufac_colors = get_summary_data()
    write_css_colors(color_dict)
