# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 17:07:42 2025

@author: michael.tu
"""
#%%
import pandas as pd
#%% example links
#https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/2010/2010_manhattan.xls
#https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/2017/2017_manhattan.xls
#%% getting the data
def get_housing(year): 
    if year > 2017: 
        excel = 'xlsx'
    else: 
        excel = 'xls'
    
    base = pd.read_excel(f'https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/{str(year)}/{str(year)}_manhattan.{excel}')
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
    housing_dict[year] = get_housing(year)
#%% concat
all_housing = pd.concat(housing_dict.values())
all_housing = all_housing.dropna(subset = 'neighborhood')
all_housing = all_housing[~all_housing['borough'].isin(['BOROUGH','BOROUGH\n'])]

all_housing['sale_date'] = pd.to_datetime(all_housing['sale_date'])
all_housing['year'] = all_housing['sale_date'].dt.year

#%% exporting
all_housing.to_csv(r'\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\all_housing_nyc.csv')

#%%
sample =all_housing.groupby('year').sample(frac=0.01, random_state=42) 
dupe_sales = all_housing[all_housing.duplicated(subset = ['block','lot'],keep=False)].sort_values(subset = ['block','lot'])
