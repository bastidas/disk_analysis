import requests
from bs4 import BeautifulSoup
import load_data
import pandas as pd
#from bokeh.io import show
from bokeh.io import show
import numpy as np
import time

def scrape_data(model,cols):
	if model == "HMS5C4040BLE640":
		target_url = "https://pcpartpicker.com/product/p7Trxr/hitachi-internal-hard-drive-hms5c4040ble6400f22146"
	if model == "ST500LM012 HN":
		target_url  = "https://pcpartpicker.com/product/Mmw323/samsung-internal-hard-drive-hnm500mbbst500lm012"
	else:
		target_url = "https://pcpartpicker.com/search/?cc=us&q=" + model
	response = requests.get(target_url, params={"limit": 2000, "offset": 0})
	print(response.url)
	soup = BeautifulSoup(response.text, "lxml")
	x = soup.find('div', attrs={'class': 'specs block'}) #Find (at most) *one*
	try:
		z = x.text.split("\n")
		zs = [s.strip() for s in z if s!=""]
		zss = [s for s in zs if s!=""]
		zss = np.asarray(zss)
		spd = {}
		for c in cols:
			i = np.where(zss == c)
			spd[c] = zss[i[0][0]+1]
		specs =  pd.DataFrame([spd.values()],columns=spd.keys())
		return specs
	except:
		pass

adf, time_strings, color_dict, colors = load_data.get_summary_data()
cols = ['Manufacturer', 'Part #','Capacity','Interface','Cache','RPM','Form Factor','Price/GB']
sdf = pd.DataFrame(columns=cols)
tried = []
for df in adf:
		df = df[df['count'] > 100 ]
		for model in df['model']:
			if model not in tried:
				tried.append(model)
				print(model, ' not in, so trying to add it')
				time.sleep(10)
				model_specs = scrape_data(model,cols)
				sdf = sdf.append(model_specs)

sdf.to_csv("drive_stats.csv")



HDS5C3030ALA630


#HMS5C4040BLE640   = "https://pcpartpicker.com/product/p7Trxr/hitachi-internal-hard-drive-hms5c4040ble6400f22146"
#ST500LM012 HN  = "https://pcpartpicker.com/product/Mmw323/samsung-internal-hard-drive-hnm500mbbst500lm012"