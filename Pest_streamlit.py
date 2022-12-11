import streamlit as st
import pandas as pd


from loads_from_url import *
from modify_dfs import *
from plot_funcs import *

import os
from pandasql import sqldf
cwd = os.getcwd()

folder_path = os.path.join(cwd,'data_files')
# folder_path = 'C:\\Users\simmt\Code1\Pesticide\Pesticide-main\data_files'
file_path = []
for x in os.listdir(folder_path):
    file_path.append(os.path.join(folder_path,x) )
    


st.title('Pesticides')


@st.cache()
def load_data(ii):
    
    print(file_path[ii])
    df = import_ods(file_path[ii])

    df2 = modify_df(df)

    return df2

data_load_state = st.text('Loading data...')
df2=load_data(2)
data_load_state.text("Loaded data (using st.cache)")

st.dataframe(df2.head())

# An optionbox- Select Product
products = df2['product'].unique()
product = st.sidebar.selectbox(
    'Select product',
     products)

# An optionbox- Select What to group by

country_or_chem = st.sidebar.selectbox(
    'What to plot',
     ['Country', 'Chemical'])
if country_or_chem=='Country':
    is_country=True
    chems = list(df2['chem_name'].unique()) 
    chems.insert(0,'all')
    chemical_country = st.sidebar.selectbox(
        'Which chemical?', chems
        )
else:
    is_country=False
    countrys = list(df2['country_of_origin'].unique()) 
    countrys.insert(0,'all')
    chemical_country = st.sidebar.selectbox(
        'Which country?', countrys
        )

# product = 'Wine'
date_low = '2010-06-01'
date_high = '2027-06-01'
data_sql = sqldf(f"""
SELECT 
    chem_name,	SUM(amount_detected) AS sum_detected, 
    country_of_origin, COUNT(*) as count_tests
FROM 
    df2
WHERE 
    product =  '{product}' AND
    date_of_sampling > '{date_low}' AND
    date_of_sampling < '{date_high}' 
    
GROUP BY
    country_of_origin, chem_name
""", locals()
)

data_sql


fig = plot_pie_by_chem(data_sql, chemical_country=chemical_country, what_to_plot='sum_detected',is_country=is_country, product=product)
st.pyplot(fig)