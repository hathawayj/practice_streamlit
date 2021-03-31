# %%
import streamlit as st 
import pandas as pd 
import altair as alt 
import numpy as np 

# %%
st.write("""
# Temples of the World

A test project using Python, Streamlit, and Altair

_J. Hathaway_

""")

dat = pd.read_csv('temples.csv')
st.line_chart(dat)
# %%
