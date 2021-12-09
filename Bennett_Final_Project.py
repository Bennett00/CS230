'''
Name: Casey Bennett
CS230: Section 5
Data: stadiums.csv
URL: Link to your web application online
Description:
This program uses Pandas, MatPlotLib, pydeck, and Streamlit.io to produce 3 queries from the NCAA stadiums data.
The first query creates a bar chart displaying the average stadium capacity for selected conferences.
The second query creates a table of stadiums for a selected division and state and displays those stadiums on a map.
The third query creates a scatter plot comparing the age of NCAA stadiums with their capacities.
'''

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pydeck as pdk
from datetime import date

# https://gist.github.com/rogerallen/1583593
us_state_to_abbrev = {
    "Default": "Choose a state",
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "Washington D.C.": "DC",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"}


# read and clean the data file
def read_data():
    df = pd.read_csv("stadiums.csv").set_index("stadium")
    # All values in div column to uppercase and all values in state column to abbreviations
    for row in df.itertuples():
        df["div"] = df["div"].str.upper()
        if len(df["state"]) > 2:
            df["state"] = df.state.replace(us_state_to_abbrev)
    df.index.rename("Stadium", inplace=True)
    df.rename(columns={"city": "City", "team": "Team Name"}, inplace=True)
    return df


# filter used for the bar chart
def filter_data1(select_conf, select_year):
    df = read_data()
    df = df.loc[df['conference'].isin(select_conf)]
    df = df.loc[df["built"].isin(select_year)]

    return df


# filter used for the map
def filter_data2(select_division, select_state):
    df = read_data()
    df = df.loc[df['state'] == select_state]
    df = df.loc[df['div'] == select_division]

    return df


# filter used for the scatter plot
def filter_data3(select_division):
    df = read_data()
    df = df.loc[df['div'] == select_division]

    return df


# list of all conferences used for bar chart multiselect box
def all_conferences():
    df = read_data()
    list_of_conferences = []
    for row in df.itertuples():
        if row.conference not in list_of_conferences:
            list_of_conferences.append(row.conference)

    return list_of_conferences


# bar chart
# functions: conf_caps, capacity_averages, and generate_bar_chart

# creates dictionary with conferences as keys and stadium capacities as values
def conf_caps(df):
    capacities = [row.capacity for row in df.itertuples()]
    conferences = [row.conference for row in df.itertuples()]
    dict = {}
    for conference in conferences:
        dict[conference] = []
    for i in range(len(capacities)):
        dict[conferences[i]].append(capacities[i])

    return dict


# function to calculate average capacity of each conference's stadium
def capacity_averages(dict_of_capacities):
    avg_dict = {}
    for key in dict_of_capacities.keys():
        avg_dict[key] = np.mean(dict_of_capacities[key])

    return avg_dict


def generate_bar_chart(dict_averages):
    plt.figure()
    x = dict_averages.keys()
    y = dict_averages.values()
    plt.bar(x, y, color="green")
    plt.xlabel("Conference")
    plt.ylabel("Average Stadium Capacity")
    plt.title("Average Stadium Capacities")

    return plt


# map function that outputs directly into Streamlit
def generate_map(df):
    map_df = df.filter(['Stadium', 'latitude', 'longitude'])
    view_state = pdk.ViewState(latitude=map_df["latitude"].mean(), longitude=map_df["longitude"].mean(), zoom=6)
    layer = pdk.Layer('ScatterplotLayer', data=map_df, get_position='[longitude, latitude]', get_radius=5000,
                      get_color=[0, 255, 65],
                      pickable=True)
    tool_tip = {'html': 'Stadium: <br><b> {Stadium} </b>', "style": {'backgroundColor': 'steelblue', 'color': 'white'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9', initial_view_state=view_state, layers=[layer], tooltip=tool_tip)
    st.pydeck_chart(map)


# function to generate scatter plot
def generate_scatter_plot(df, trend_line):
    plt.figure()
    current_date = date.today()
    current_year = current_date.year
    year_list = [row.built for row in df.itertuples()]
    x = []
    for i in year_list:
        age = current_year - i
        x.append(age)
    y = [row.capacity for row in df.itertuples()]
    plt.scatter(x, y, marker='H', color='g', s=40)
    plt.xlabel("Stadium Age in Years")
    plt.ylabel("Capacity")
    plt.title("Capacity vs. Stadium Age")
    # add trend line to scatter plot if user selects "Yes" from radio button
    if trend_line == "Yes":
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        plt.plot(p(x))

    return plt


def main():
    st.sidebar.image("logo.png", width=100)
    st.title("NCAA Football Stadiums")
    st.image(["football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png",
              "football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png",
              "football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png"], width=39)

    # bar chart
    st.subheader('Bar Chart')
    st.sidebar.subheader("Select options for the bar chart: ")
    conferences = st.sidebar.multiselect("Conferences: ", all_conferences())
    st.sidebar.caption("Range of year built for stadiums:")
    lower_year = st.sidebar.slider("Lower:", 1895, 2014)
    upper_year = st.sidebar.slider("Upper:", 1895, 2014)
    year_range = [n for n in range(lower_year, upper_year + 1)]
    st.sidebar.write("\n\n")

    # generating bar chart based on sidebar input
    bar_data = filter_data1(conferences, year_range)
    if bar_data.empty:
        st.write("There are no stadiums within your selected year range.")
    else:
        st.pyplot(generate_bar_chart(capacity_averages(conf_caps(bar_data))))

    st.write("\n")
    st.image(["football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png",
              "football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png",
              "football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png"], width=39)  # football divider

    # Table and map
    st.subheader('Table and Map')
    st.sidebar.subheader("Select options for the table and map:")
    division = st.sidebar.radio("Division:", ("FBS", "FCS"))
    state = st.sidebar.selectbox("State: ", us_state_to_abbrev.values())
    st.sidebar.write("\n\n")

    # generating table and map based on sidebar input
    map_data = filter_data2(division, state)
    if map_data.empty and state == "Choose a state":
        st.write("Select options to display a table and a map.")
    elif map_data.empty and state != "Choose a state":
        for s in us_state_to_abbrev:
            if state != "Choose a state" and state == us_state_to_abbrev[s]:
                st.write(f'There are no {division} stadiums in {s}.')
    else:
        table = map_data[["City", "Team Name"]]
        table = table.sort_values(["Stadium"], ascending=[True])
        count = 0
        for row in table.itertuples():
            count += 1
        for s in us_state_to_abbrev:
            if state == us_state_to_abbrev[s]:
                st.write(f'There are {count} {division} stadiums in {s}:')
        st.write(table)
        st.write("\n")
        generate_map(map_data)

    st.write("\n")
    st.image(["football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png",
              "football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png",
              "football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png"], width=39)  # football divider

    # scatter plot
    st.subheader('Scatter Plot')
    st.sidebar.subheader("Select options for the scatter plot:")
    division = st.sidebar.text_input("Enter a division (FBS or FCS): ").upper()
    trend = st.sidebar.radio("Show trend line:", ('No', 'Yes'))

    # generating scatter plot based on sidebar input
    scatter_data = filter_data3(division)
    if division != " " and division != "FBS" and division != "FCS":
        st.write("The division must be FBS or FCS.")
    if scatter_data.empty:
        st.write("Select options to display a scatter plot.")
    else:
        st.pyplot(generate_scatter_plot(scatter_data, trend))

    st.write("\n")
    st.image(["football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png",
              "football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png",
              "football1.png", "football1.png", "football1.png", "football1.png", "football1.png", "football1.png"], width=39)  # football divider


main()









