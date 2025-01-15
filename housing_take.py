# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 17:07:42 2025

@author: michael.tu
"""
#%%
import pandas as pd
import numpy as np
#%% example links
#https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/2010/2010_manhattan.xls
#https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/2017/2017_manhattan.xls
#%% getting the data
def get_housing(borough,year): 
    if year > 2017: 
        excel = 'xlsx'
    else: 
        excel = 'xls'
    
    base = pd.read_excel(f'https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/{str(year)}/{str(year)}_{borough}.{excel}')
    base.columns = ['borough', 'neighborhood', 'building_class_category',
           'tax_class_at_present', 'block', 'lot', 'ease-ment',
           'building_class_at_present', 'address', 'apartment_number', 'zip_code',
           'residentialunits', 'commercialunits', 'total_units',
           'land_square_feet', 'gross_square_feet', 'year_built',
           'tax_class_at_time_of_sale', 'building_classat_time_of_sale',
           'sale_price', 'sale_date']
    #base.columns = base.columns.str.lower().str.strip()
    #base.columns = base.columns.str.replace('\n','')
    #base.columns = base.columns.str.replace(' ','_')
    
    relevant_columns = ['borough', 'neighborhood', 'address','apartment_number','building_class_category',
                        'building_class_at_present','block','lot','zip_code','residentialunits',
                        'commercialunits','total_units',
                        'land_square_feet', 'gross_square_feet', 'year_built','tax_class_at_time_of_sale',
                        'sale_price', 'sale_date']

    out = base[relevant_columns]
    print('Done with' + str(year))
    return out

housing_dict = {}
for year in range(2010,2024): 
    housing_dict[year] = get_housing('manhattan',year)
#%% concat
all_housing = pd.concat(housing_dict.values())
all_housing = all_housing.dropna(subset = 'neighborhood')
all_housing = all_housing[~all_housing['borough'].isin(['BOROUGH','BOROUGH\n'])]

all_housing['sale_date'] = pd.to_datetime(all_housing['sale_date'])
all_housing['year'] = all_housing['sale_date'].dt.year
#%% address cleaning
def clean_apt(address): 
    if len(address.split(",")) > 1: #if splittable
        apt = address.split(",")[-1]
    else: 
        apt = address
    return apt
#%% Cleaning Apartment Number

#specifically aprtment number
all_housing['apartment_number'] = all_housing['apartment_number'].str.strip()
all_housing['apartment_number'] = all_housing['apartment_number'].astype(str)

#where apt number is empty or nan fix
all_housing['apartment_number'] = np.where(all_housing['apartment_number'].isin(['','nan']),all_housing['address'].apply(clean_apt),all_housing['apartment_number'])
all_housing['apartment_number'] = all_housing['apartment_number'].str.strip()
all_housing['lot'] = all_housing['lot'].astype(str).str.strip()
all_housing['block'] = all_housing['block'].astype(str).str.strip()
all_housing['block_lot_num'] = all_housing['block'] + '_' + all_housing['lot'] + '_' + all_housing['apartment_number']

# limiting to A,B,C,D,R,S - https://www.nyc.gov/assets/finance/jump/hlpbldgcode.html
all_housing = all_housing[(all_housing['building_class_at_present'].str[0].isin(['A','B','C','D','S'])) | (all_housing['building_class_at_present'].isin(['R1','R2',
                                                                                                                                                    'R3','R4','R6',
                                                                                                                                                              'R6','R7','R8','R9']))]

#limiting to just < 3 units - basically single transactions
all_housing = all_housing[all_housing['total_units'] < 3] 
# cleaning neighborhood
all_housing['neighborhood'] = all_housing['neighborhood'].astype(str).str.strip()

a_test = all_housing[all_housing.duplicated(subset = ['sale_price','sale_date'])]
#%% exporting
all_housing.to_csv(r'\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\all_housing_manhattan_2010_2023.csv')

#%% EDA
eda = all_housing[all_housing['total_units'] < 3] 
#excluding transfers for no cash considerations
eda = eda[eda['sale_price']>=1000]
#dropping those with same exact sale price on same day and block...
eda = eda[~eda.duplicated(subset = ['sale_price','sale_date','block'])]
eda.to_csv(r'\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\manhattan_limited.csv')


dupe_sales = eda[eda.duplicated(subset = ['apartment_number','block','lot'],keep=False)].sort_values(by = ['block','lot','apartment_number'])
dupe_sales.to_csv(r'\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\manhattan_dupe_sales.csv')

#%%
#how many properties exchanged hands?  21834 Changed Hands in the period 2010 - 2023
print(dupe_sales['block_lot_num'].nunique())

#by neighborhood? 
neighborhood_sales = dupe_sales['neighborhood'].value_counts().reset_index()
"""
Most by volume is UES and UWS. Followed then by Chelsea and Midtown.
"""

#by sale price? by neighborhood and sale price? 
price_by_loc = dupe_sales.groupby('block_lot_num').agg({'sale_price':'mean','lot':'count'}).reset_index()
print(price_by_loc['sale_price'].median())
price_by_neighborhood = dupe_sales.groupby('neighborhood').agg({'sale_price':'mean','lot':'count'}).reset_index().sort_values('sale_price',ascending = False).reset_index(drop=True)
print(price_by_neighborhood['sale_price'].median())

#by neighborhood and year
price_by_neighborhood_yr = dupe_sales.groupby(['neighborhood','year']).agg({'sale_price':'median','lot':'count'}).reset_index().sort_values('sale_price',ascending = False).reset_index(drop=True)

