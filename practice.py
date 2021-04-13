# %%
# import sys
# !{sys.executable} -m pip install streamlit vega_datasets
# %%
import streamlit as st 
import pandas as pd 
import altair as alt 
import numpy as np 
import base64

from vega_datasets import data

# %%
st.set_page_config(page_title="Temples of the Restoration", layout='wide')

source = alt.topo_feature(data.world_110m.url, 'countries')
states = alt.topo_feature(data.us_10m.url, feature='states')

sphere = alt.sphere()
graticule = alt.graticule()

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
            year = lambda x: x.Announcement.dt.year,
            Temple=lambda x: x.Temple.str.replace(' Temple', ''),
            Announcement=lambda x: x.Announcement.dt.date,
            Groundbreaking=lambda x: x.Groundbreaking.dt.date,
            Dedication=lambda x: x.Dedication.dt.date,  
        )
            )
    return df

dat = load_data()

@st.cache
def dat_totals():
    dat_totals = dat \
        .filter(['year','SquareFootage', 'Acreage', 'Announcement']) \
        .groupby('year') \
        .agg(
            counts = ('year', 'count'),
            sqft = ('SquareFootage', 'sum'),
            acre = ('Acreage', 'sum')
        )
    return dat_totals

dat_tots = dat_totals()

all_years = pd.DataFrame({'year':range(1847, 2015)})

dat_bar = all_years \
    .join(dat_tots, on = 'year') \
    .fillna(0) \
    .assign(
        counts = lambda x: x.counts.cumsum(),
        sqft = lambda x: x.sqft.cumsum(),
        acre = lambda x: x.acre.cumsum()
    )

cnames = dat.Country.sort_values(ascending=False).unique().tolist()
snames = dat.query("Country == 'United States'").State.unique().tolist()
projections = ['naturalEarth1', 'orthographic', 'equirectangular', 'mercator']

ydetails = {'SquareFootage':"Size (Sq.Ft.)", 
    'Acreage': "Size (Acres)", 'InstructionRooms':"Endowment Rooms",
    'SealingRooms':"Sealing rooms"}

ycolumns = list(ydetails.keys())

# %%

st.sidebar.image('rexburg.jpg')
st.sidebar.write('A visual project using Python, Streamlit, and Altair')
age = st.sidebar.slider("Choose your Birth Year:", min_value=1830,
    max_value=2015, value=1830, step = 1)
ybar = st.sidebar.radio("Choose your bar chart y-axis", ['counts', 'sqft', 'acre'])
yaxis = st.sidebar.radio("Choose your scatterplot y-axis", ycolumns)
proj = st.sidebar.selectbox("Choose your world projection.", projections)
state_select = st.sidebar.selectbox("Choose your state", snames)

age_date = pd.to_datetime(str(age))

dat_filter = dat.query("Announcement > @age_date")


# %%
st.write("""
# Temples of the World
## _J. Hathaway_

-------

This display lets you interact with charts about temples from The Church of Jesus Christ of Latter-day Saints.
_The data is taken from [churchofjesuschristtemples.org](https://churchofjesuschristtemples.org/statistics/).\
You can expand any chart to fill the screen by hovering in the top-right corner of the chart._

-------
""")

st.write("#### _" + str(dat_filter.Temple.size) + "_ have been built since your birth year of " + str(age) + ".")
st.write("_As you select your birth year on the side menu the counts after your birth will highlight. You can also\
    change the y-axis using the bar chart radio buttons._")

# %%
bc = alt.Chart(dat_bar \
    .assign(
        youryear = lambda x: np.where(x.year > age, "After", "Before"))) \
    .encode(
        alt.X('year', axis=alt.Axis(format=".0f")), 
        y = ybar,
        color = alt.Color('youryear')) \
    .mark_bar()

st.altair_chart(bc.configure_axis(labelFontSize=18, 
    titleFontSize=18) \
    .interactive(), use_container_width=True)

# %%
c = (alt.Chart(dat_filter)
    .encode(
        alt.X('Announcement:T', scale=alt.Scale(padding=20), 
            axis=alt.Axis(title="Announcement Date")), 
        alt.Y(yaxis, scale=alt.Scale(padding=1), axis=alt.Axis(title=ydetails[yaxis])),
        tooltip=['Temple', yaxis]
        )
    .mark_circle(size = 85)
    )

d = c.encode(
        color = alt.Color('Country', legend=None, scale=alt.Scale(domain = cnames))) + \
        c.transform_loess('Announcement', yaxis, bandwidth = .3) \
            .mark_line(size = 2, color = 'black', opacity=.6)

st.write("_This chart will scale based on your birth year as well. Using the scatterplot radio buttons will\
    allow you to change the y-axis. You can also hover over the points to see the temple name and square footage._")

st.altair_chart(d.configure_axis(labelFontSize=18, 
    titleFontSize=18) \
    .interactive(), use_container_width=True)

# %%
hover = alt.selection(type='single', on='mouseover', nearest=True,
                      fields=['Latitude', 'Longitude'])

bt = alt.Chart(dat_filter).encode(
    longitude='Longitude:Q',
    latitude='Latitude:Q'
)

bpoints = bt.encode(
    color=alt.condition(~hover, alt.value('red'), alt.value('black')),
    fill=alt.condition(~hover, alt.value('red'), alt.value('black')),
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


st.write('_This map shows all the temples built since your selected birth year.\
    Maps are unique in that everyone needs a projection to move from a globe to a 2D map.\
    You can change how the globe is projected using the side menu._')
st.altair_chart(base.properties(title="Temples of the World"), use_container_width=True)


# %%
usa = alt.Chart(states).mark_geoshape(
    fill='lightgray',
    stroke='white'
)

dat_state = dat_filter.query('Country == "United States"').assign(
    state = lambda x: np.where(x.State == state_select, state_select, "Other"),
    counts = lambda x: np.where(x.State == state_select, 1, 0))

bt_usa = alt.Chart(dat_state).encode(
    longitude='Longitude:Q',
    latitude='Latitude:Q'
)

bpoints_usa = bt_usa.encode(
    fill=alt.condition(~hover, "state", alt.value('black')),
    size=alt.condition(~hover, alt.value(50), alt.value(200)),
).add_selection(hover)

btext = bt_usa.encode(
    alt.Text('Temple', type='nominal'),
    color=alt.value('black'),
    opacity=alt.condition(~hover, alt.value(0), alt.value(1))
).mark_text(align='right', dy=-5, fontWeight=500, fontSize = 12)


base_usa = alt.layer(
    usa,
    bpoints_usa.mark_circle(),
    btext
).project('albersUsa').properties(width='container', height=400).configure_view(stroke=None)

st.write('_This map shows all the temples built in the U.S. since your selected birth year.\
    You can see the count of temples in a specific state by picking your state in the side menu._')
st.altair_chart(base_usa.properties(title="Temples of the USA: " + str(dat_state.counts.sum()) + " in " + state_select), use_container_width=True)


# %%
st.write('_Finally, this table displays the data used for the above graphics._')

st.dataframe(dat_filter.style.set_precision(0))

csv = dat_filter.to_csv(index=False)
b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
st.markdown(href, unsafe_allow_html=True)
