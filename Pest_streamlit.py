import streamlit as st
import pandas as pd

import src.data_loading.loads_from_url as lfu
import src.data_cleaning.modify_dfs as mdf
import src.data_visualisation.plot_funcs as pfs

import os
from pandasql import sqldf
cwd = os.getcwd()

folder_path = os.path.join(cwd, 'data')



st.title('Pesticides')



data_load_state = st.text('Loading data...')

@st.cache
def load_dfs():
    all_dfs = pd.read_csv('./data/combined_df.csv')
    return all_dfs

all_dfs = load_dfs()
data_load_state.text("Loaded data (using st.cache)")

st.dataframe(all_dfs.head())

# An optionbox- Select Product    
products = all_dfs['product'].unique()
product = st.sidebar.selectbox(
    'Select product',
    products)

# An optionbox- Select What to group by
country_or_chem = st.sidebar.selectbox(
    'What to plot',
     ['Country', 'Chemical'])

if country_or_chem=='Country':
    is_country=True
    chems = list(all_dfs['chem_name'].unique()) 
    chems.insert(0,'all')

    chemical_country = st.sidebar.selectbox(
        'Which chemical?', chems
    )
else:

    is_country=False
    countrys = list(all_dfs['country_of_origin'].unique()) 
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
    all_dfs
WHERE 
    product =  '{product}' AND
    date_of_sampling > '{date_low}' AND
    date_of_sampling < '{date_high}' 
    
GROUP BY
    country_of_origin, chem_name
""", locals()
)

data_sql


fig = pfs.plot_pie_by_chem(data_sql, chemical_country=chemical_country,
                           what_to_plot='sum_detected', is_country=is_country, product=product)
st.pyplot(fig)
