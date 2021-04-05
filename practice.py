# %%
# import sys
# !{sys.executable} -m pip install streamlit
# %%
import streamlit as st 
import pandas as pd 
import altair as alt 
import numpy as np 

# %%

st.set_page_config(page_title="Temples of the Restoration")


st.write("""
# Temples of the World

A visual project using Python, Streamlit, and Altair

_J. Hathaway_

""")

@st.cache
def load_data():
    df = (pd.read_csv('temples.csv')
        .query('not SquareFootage.isnull()')
        .filter(['Temple', 'Country', 'State', 'City', 
            'SquareFootage', 'InstructionRooms', 'SealingRooms',
            'BaptismRooms', 'Acreage', 'Latitude', 'Longitude', 
            'Announcement', 'Groundbreaking', 'Dedication']))
    return df

dat = load_data()
cnames = dat.Country.sort_values(ascending=False).unique().tolist()

st.write(dat.style.set_precision(0))

age = st.sidebar.slider("Choose your Birth Year: ", min_value=1930,
    max_value=2020, value=2000, step = 1)

country = st.sidebar.multiselect("Where were you born?", 
                         cnames)
# %%
c = (alt.Chart(dat)
    .encode(alt.X('Announcement:T'), 
        alt.Y('SquareFootage'))
    .mark_circle()
    .interactive())

st.altair_chart(c, use_container_width=True)