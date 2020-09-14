import requests
import ast
import pandas as pd

bbr_bygning_url = "https://services.datafordeler.dk//BBR/BBRPublic/1/REST/bygning?"
bbr_enhed_url = "https://services.datafordeler.dk//BBR/BBRPublic/1/REST/enhed?"
bbr_ejendomsrelation_url = "https://services.datafordeler.dk//BBR/BBRPublic/1/REST/ejendomsrelation?"
bbr_sag_url = "https://services.datafordeler.dk//BBR/BBRPublic/1/REST/bbrsag?"
bbr_grund_url = "https://services.datafordeler.dk//BBR/BBRPublic/1/REST/grund?"
bbr_tekniskanlaeg_url = "https://services.datafordeler.dk//BBR/BBRPublic/1/REST/tekniskanlaeg?"


pars = {'username': 'XBNOBAOZNU', 
'password': 'WillGriggsOn-4ire'}

r = requests.get(bbr_tekniskanlaeg_url, params=pars)
r = ast.literal_eval(r.text)

df = pd.DataFrame(r)

df.iloc[0, :]


## Dokumentation for BBR 
# https://confluence.datafordeler.dk/pages/viewpage.action?pageId=16056582