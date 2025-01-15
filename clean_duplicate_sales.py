# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 14:03:56 2025

@author: michael.tu
"""

#%%
import pandas as pd

#%% import the raw duplicates
base = pd.read_csv(r"\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\manhattan_dupe_sales.csv")

#limit variables
variables = ['neighborhood', 'address', 'apartment_number', 'zip_code','building_class_at_present','sale_price', 'sale_date', 'year','block_lot_num']

temp = base[variables]
#limit to UES; non-Roosevelt Island
temp = temp[(temp['neighborhood'].isin(['UPPER EAST SIDE (59-79)','UPPER EAST SIDE (79-96)',
                                        'UPPER EAST SIDE (96-110)'])) & (temp['zip_code']!=10044)]
#%% dropping those sold 5+ times or 1 time (on date)
a = temp.groupby('block_lot_num')['sale_date'].nunique()    
temp = temp.merge(a,on = 'block_lot_num',suffixes = ['','_count'])
temp = temp[(temp['sale_date_count'] < 5) & (temp['sale_date_count']>1)]

#%% arranging where there's a cross join on every combo of sales
temp['sale_date'] = pd.to_datetime(temp['sale_date'])
temp2 = temp[['block_lot_num','sale_price','sale_date','year']]

combo = pd.merge(temp,temp2,how = 'left',on = 'block_lot_num',suffixes = ['_1','_2'])
combo = combo[combo['sale_date_1']< combo['sale_date_2']]

#%% appreciation calculation
cpiu =pd.read_excel(r"\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\cpiu_housing_monthly.xlsx")
cpiu['month'] = pd.to_datetime(cpiu['observation_date']).dt.month
cpiu['year'] = pd.to_datetime(cpiu['observation_date']).dt.year
cpiu['cpi'] = cpiu['CPIHOSNS'] / 247.942 #value in jan 2017

combo['sale_month_1'] = combo['sale_date_1'].dt.month
combo['sale_month_2'] = combo['sale_date_2'].dt.month

combo = combo.merge(cpiu[['month','year','cpi']],left_on = ['sale_month_1','year_1'],right_on = ['month','year'],
                    how = 'left').rename({'cpi':'cpi_1'}).drop(columns = ['month','year'])
combo = combo.merge(cpiu[['month','year','cpi']],left_on = ['sale_month_2','year_2'],right_on = ['month','year'],
                    how = 'left').rename({'cpi':'cpi_2'}).drop(columns = ['month','year'])

#first 
combo['appr_1'] =(combo['sale_price_2'] / combo['cpi_y'])/(combo['sale_price_1'] / combo['cpi_x']) 

#annualized
combo['appr_2'] = combo['appr_1'] ** (1/ (combo['year_2']-combo['year_1']))

#%% Get third appreciation metric
man_lim = pd.read_csv(r'\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\manhattan_limited.csv')
ues = man_lim[man_lim['neighborhood'].isin(['UPPER EAST SIDE (59-79)','UPPER EAST SIDE (79-96)',
                                        'UPPER EAST SIDE (96-110)'])]

ues = ues[ues['zip_code']!=10044]

ues_index = ues.groupby('year').agg({'sale_price':'median'}).reset_index().rename(columns = {'sale_price':'sale_price_ind'})
combo = combo.merge(ues_index,left_on = 'year_1',right_on = 'year',how = 'left').drop(columns = 'year')
combo = combo.merge(ues_index,left_on = 'year_2',right_on = 'year',how = 'left').drop(columns = 'year')

combo['appr_3'] = (combo['sale_price_2']/combo['sale_price_1']) * (combo['sale_price_ind_y'] / combo['sale_price_ind_x'])

#basically keep the first duplicate sale 
combo = combo.sort_values(by = 'sale_date_2').drop_duplicates(subset = ['sale_date_1','block_lot_num'],keep='first')
#%% Get output
out = combo.drop(columns = ['sale_month_1', 'sale_month_2', 'cpi_x',
'cpi_y','sale_price_ind_x', 'sale_price_ind_y','sale_date_count'])

#cut outliers
lower = out['appr_1'].quantile(.01)
upper = out['appr_1'].quantile(.99)

out = out[(out['appr_1'] > lower) & (out['appr_1'] < upper)]

out.to_excel(r'\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\repeat_sales_ues_cleaned_w_appreciation.xlsx',index=False)

