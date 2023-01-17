import streamlit as st
import pandas as pd
import os
from streamlit_folium import st_folium

import src.utils.map_utils as mu

st.title('Pesticide- Map Plots')



data_load_state = st.text('Loading data...')

@st.cache
def load_dfs():
    df = pd.read_csv('./data/combined_df.csv', index_col=0)
    return df

df = load_dfs()
data_load_state.text("Loaded data (using st.cache)")

address_col = "address_area"
df_comb = df.groupby(address_col,as_index=False).mean(numeric_only = True)

m = mu.plot_map(df, 
             what_to_plot='amount_pc',region_to_plot=address_col,
             json_path=os.path.join('.//src//utils//map_data//combined_json.json'),
             longitude=-3.1, latitude=54.1)

st_data = st_folium(m, width=725)