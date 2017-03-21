import pandas as pd
import numpy as np


time_strings = ['2014 Q1', '2014 Q2', '2014 Q3', '2014 Q4',
    '2015 Q1', '2015 Q2' , '2015 Q3', '2015 Q4',
    '2016 Q1', '2016 Q2' , '2016 Q3', '2016 Q4']


time_indexer = dict(zip(time_strings, range(len(time_strings))))

dfiles = ['2014_Q1.csv', '2014_Q2.csv', '2014_Q3.csv', '2014_Q4.csv',
    '2015_Q1.csv', '2015_Q2.csv' , '2015_Q3.csv', '2015_Q4.csv',
    '2016_Q1.csv', '2016_Q2.csv', '2016_Q3.csv', '2016_Q4.csv']

adf = []
for file in dfiles:
	#df = pd.read_csv(tf)
	tf = "data/" + file
	#print(tf)
	df = pd.read_csv(tf)
	#print(df.head)
	#print(df.columns)
	del df['Unnamed: 0'] # delete malformed index row
	adf.append(df)

#adf = np.asarray(adf)
#print(np.shape(adf))


print(adf[time_indexer['2016 Q2']])



for i in range(len(adf)):
	counts = np.sort(adf[i]['count'])[::-1]
	models = [x for (y, x) in sorted(zip(adf[i]['count'], adf[i]['model']))][::-1]
	print(counts[0:5], models[0:5])

#time_strings = ['2014 Q1', '2014 Q2', '2014 Q3', '2014 Q4',


#import pandas as pd
#import numpy as np
#from bokeh.palettes import Spectral11
#from bokeh.plotting import figure, show, output_file
#output_file('temp.html')

#toy_df = pd.DataFrame(data=np.random.rand(5,3), columns = ('a', 'b' ,'c'), index = pd.DatetimeIndex(start='01-01-2015',periods=5, freq='d'))   

#numlines=len(toy_df.columns)
#mypalette=Spectral11[0:numlines]

#p = figure(width=500, height=300, x_axis_type="datetime") 
#p.multi_line(xs=[toy_df.index.values]*numlines,
#                ys=[toy_df[name].values for name in toy_df],
#                line_color=mypalette,
#                line_width=5)
#show(p)