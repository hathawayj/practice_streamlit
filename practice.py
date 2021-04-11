# %%
# import sys
# !{sys.executable} -m pip install streamlit vega_datasets
# %%
import streamlit as st 
import pandas as pd 
import altair as alt 
import numpy as np 

from vega_datasets import data


# %%

st.set_page_config(page_title="Temples of the Restoration")

st.sidebar.image('rexburg.jpg')

st.write("""
# Temples of the World

A visual project using Python, Streamlit, and Altair

_J. Hathaway_

""")

@st.cache
def load_data():
    df = (pd.read_csv('temples.csv', 
            parse_dates=['Announcement', 'Groundbreaking','Dedication'])
        .query('not SquareFootage.isnull()')
        .filter(['Temple', 'Country', 'State', 'City', 
            'SquareFootage', 'InstructionRooms', 'SealingRooms',
            'BaptismRooms', 'Acreage', 'Latitude', 'Longitude', 
            'Announcement', 'Groundbreaking', 'Dedication'])
        .assign(
            Temple=lambda x: x.Temple.str.replace(' Temple', ''),
            Announcement=lambda x: x.Announcement.dt.date,
            Groundbreaking=lambda x: x.Groundbreaking.dt.date,
            Dedication=lambda x: x.Dedication.dt.date  
        )
            )
    return df

dat = load_data()
cnames = dat.Country.sort_values(ascending=False).unique().tolist()

age = st.sidebar.slider("Choose your Birth Year:", min_value=1830,
    max_value=2020, value=1830, step = 1)

age_date = pd.to_datetime(str(age))

projections = ['naturalEarth1', 'orthographic', 'equirectangular', 'mercator']

proj = st.sidebar.selectbox(projections[2], projections)
# %%
dat_filter = dat.query("Announcement > @age_date")

st.write("-------")

st.write("__" + str(dat_filter.Temple.size) + "__ have been built since year you were born.")

st.dataframe(dat_filter.style.set_precision(0))
# %%
c = (alt.Chart(dat_filter)
    .encode(
        alt.X('Announcement:T', scale=alt.Scale(padding=20), 
            axis=alt.Axis(title="Announcement Date")), 
        alt.Y('SquareFootage', scale=alt.Scale(padding=1), axis=alt.Axis(title="Size of Temple"))
        )
    .mark_circle(size = 85))

d = c.encode(
        color = alt.Color('Country', legend=None, scale=alt.Scale(domain = cnames))) + \
        c.transform_loess('Announcement', 'SquareFootage', bandwidth = .3) \
            .mark_line(size = 2, color = 'black', opacity=.6)

st.altair_chart(d.configure_axis(labelFontSize=18, titleFontSize=18).interactive(), use_container_width=True)

# %%
source = alt.topo_feature(data.world_110m.url, 'countries')
sphere = alt.sphere()
graticule = alt.graticule()

hover = alt.selection(type='single', on='mouseover', nearest=True,
                      fields=['Latitude', 'Longitude'])

bt = alt.Chart(dat_filter).encode(
    longitude='Longitude:Q',
    latitude='Latitude:Q'
)

bpoints = bt.encode(
    color=alt.condition(~hover, alt.value('black'), alt.value('black')),
    fill=alt.condition(~hover, alt.value('black'), alt.value('darkgrey')),
    size=alt.condition(~hover, alt.value(10), alt.value(200)),
).add_selection(hover)

btext = bt.encode(
    alt.Text('Temple', type='nominal'),
    color=alt.value('black'),
    opacity=alt.condition(~hover, alt.value(0), alt.value(1))
).mark_text(align='right', dy=-5, fontWeight=500, fontSize = 12)



base = alt.layer(
    alt.Chart(sphere).mark_geoshape(fill='#f0f8ff'),
    alt.Chart(graticule).mark_geoshape(stroke='lightgrey', strokeWidth=0.5),
    alt.Chart(source).mark_geoshape(fill='#f9f9f9', stroke='darkgrey'),
    bpoints.mark_circle(),
    btext
).project(
    proj
).properties(width='container', height=400).configure_view(stroke=None)


# base = alt.Chart(source).mark_geoshape(
#     fill='#666666',
#     stroke='white'
# ).properties(
#     width=600,
#     height=360
# )



st.altair_chart(base.properties(title="Temples of the World"), use_container_width=True)


