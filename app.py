# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import random


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server


# Load data
df = pd.read_csv('/home/david/Documents/learning_repositories/ih_datamadpt0420_project_m2/data/diamonds_train.csv')

# Multi-dropdown options
filter_options = df.select_dtypes(include=np.number).columns.to_list()


# Create global chart template
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("ironH.jpg"),
                            id="ironhack-image",
                            style={
                                "height": "150px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Data Analytics April 2020 part time - Project m2",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Diamonds Overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://plot.ly/dash/pricing/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Control Pane",
                            className="control_label",
                        ),
                        html.P(
                            "Delimit by price:",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="price_slider",
                            min=df['price'].min(),
                            max=df['price'].max(),
                            value=[df['price'].min(), df['price'].max()],
                            tooltip={'always_visible': True,
                                     'placement': 'bottomLeft'},
                            className="dcc_control",
                        ),
                        html.P("Color filter:", className="control_label"),
                        dcc.RadioItems(
                            id="color_selector",
                            options=[
                                {"label": "All", "value": "all"},
                                {"label": "J", "value": "J"},
                                {"label": "H", "value": "H"},
                                {"label": "G", "value": "G"},
                                {"label": "D", "value": "D"},
                                {"label": "F", "value": "F"},
                                {"label": "E", "value": "E"},
                                {"label": "I", "value": "I"},
                            ],
                            value="all",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        html.P("Choose columns:", className="control_label"),
                        dcc.Dropdown(
                            id="type_filter",
                            options=[{'label': elem, 'value': elem} for elem in filter_options],
                            multi=True,
                            value=['price'],
                            className="dcc_control",
                        ),

                        html.P("Filter by well type:", className="control_label"),
                        dcc.RadioItems(
                            id="well_type_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Productive only ", "value": "productive"},
                                {"label": "Customize ", "value": "custom"},
                            ],
                            value="productive",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="well_types",
                            #options=well_type_options,
                            multi=True,
                            #value=list(WELL_TYPES.keys()),
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="main_title"), html.P("Overview")],
                                    id="Overview",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [dcc.RadioItems(
                                        id="table_type",
                                        options=[
                                            {"label": "Data Frame (head)", "value": "dataframe"},
                                            {"label": "Data Frame (full)", "value": "dataframefull"},
                                            {"label": "Describe", "value": "describe"},
                                            {"label": "Uniques", "value": "uniques"}
                                        ],
                                        value="dataframe",
                                        labelStyle={"display": "inline-block"},
                                        className="dcc_control",
                                    )],
                                    className="mini_container",
                                    id="tables_type"
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="main_graph")],
                            id="mainGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="first_left_graph", figure={})],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="individual_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="pie_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="aggregate_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

# Callback for main overview

@app.callback(
    Output(component_id='main_graph', component_property='figure'),
    [Input(component_id='table_type', component_property='value'),
     # Input(component_id='price_slider', component_property='value'),
     ])
def update_main_graph(table_type):
    dff = df.copy()
    fig = go.Figure()
    
    if table_type == "dataframe":
        dff = dff.head(10)
        fig.add_trace(go.Table(
            header=dict(values=list(dff.columns)),
            cells=dict(values=[dff[elem] for elem in dff.columns])
        )
        )
    elif table_type == "describe":
        dff = dff.describe(include='all')
        dff.insert(loc=0, column='Stats', value=list(dff.index))
        fig.add_trace(go.Table(
            header=dict(values=list(dff.columns)),
            cells=dict(values=[dff[elem] for elem in dff.columns])
        )
        )
    fig.update_layout(title_text='Overview',
                      plot_bgcolor='#F9F9F9',
                      paper_bgcolor='#F9F9F9',)
    return fig


@app.callback(
    Output(component_id='first_left_graph', component_property='figure'),
    [Input(component_id='type_filter', component_property='value'),
     Input(component_id='price_slider', component_property='value'),
     Input(component_id='color_selector', component_property='value')])
def update_graph(type_filter, price_slider, color_selector):

    dff = df.copy()

    if color_selector == 'all':
        dff = dff.loc[dff['price'].isin(range(price_slider[0], price_slider[1]))]
    else:
        dff = dff.loc[(dff['price'].isin(range(price_slider[0], price_slider[1]))) & (df['color'] == color_selector)]

    fig = go.Figure()
    for elem in type_filter:
        hex_number = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        hex_number = '#' + hex_number

        fig.add_trace(go.Histogram(x=dff[f'{elem}'],
                                   marker_color=hex_number,
                                   name=f'{elem}',
                                   opacity=0.75,
                                   nbinsx=20
        ))
        fig.update_layout(title_text='Overview',
                          plot_bgcolor='#F9F9F9',
                          paper_bgcolor='#F9F9F9',
                          bargap=0.2,
                          bargroupgap=0.1,
                          yaxis=dict(title_text='Count of diamonds',
                                     titlefont=dict(size=20),
                                     range=[0, 5000],
                                     dtick=500
                                     ),
                          xaxis=dict(title_text=f'{elem}',
                                     titlefont=dict(size=20),

                                     )

                         )
    fig.update_yaxes(automargin=True)

    return fig


# Main
if __name__ == "__main__":
    app.run_server(debug=True)