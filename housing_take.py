# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 17:07:42 2025

@author: michael.tu
"""
#%%
import pandas as pd

#%% getting the data
def get_housing(year): 
    base = pd.read_excel(f'https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/{str(year)}/{str(year)}_manhattan.xlsx')
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
    
    relevant_columns = ['borough', 'neighborhood', 'address','building_class_category',
                        'building_class_at_present','block','lot','zip_code','residentialunits',
                        'commercialunits','total_units',
                        'land_square_feet', 'gross_square_feet', 'year_built','tax_class_at_time_of_sale',
                        'sale_price', 'sale_date']

    out = base[relevant_columns]
    print('Done with' + str(year))
    return out

housing_dict = {}
for year in range(2018,2024): 
    housing_dict[year] = get_housing(year)
#%% concat
all_housing = pd.concat(housing_dict.values())
all_housing = all_housing.dropna(subset = 'neighborhood')
all_housing = all_housing[~all_housing['borough'].isin(['BOROUGH','BOROUGH\n'])]

all_housing['sale_date'] = pd.to_datetime(all_housing['sale_date'])
all_housing['year'] = all_housing['sale_date'].dt.year

#%% exporting
all_housing.to_csv(r'\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\all_housing_nyc.csv')
