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
import webbrowser

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server


# Load data
df = pd.read_csv('/home/david/Documents/learning_repositories/ih_datamadpt0420_project_m2/data/diamonds_train.csv')
df['volume'] = df['x'] * df['y'] * df['z']
# Multi-dropdown options
numeric_filter_options = df.select_dtypes(include=np.number).columns.to_list()
categorical_filter_options = df.select_dtypes(include=np.object).columns.to_list()
all_filter_options = df.columns.to_list()

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

                        html.P("Choose variable:", className="control_label"),
                        dcc.Dropdown(
                            id="all_variable_filter",
                            options=[{'label': elem, 'value': elem} for elem in all_filter_options],
                            multi=True,
                            value=['clarity', 'cut'],
                            className="dcc_control",
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
                        html.Div(
                            #[html.H6(id="sub_Graphs_title"), html.P("Sub Graphs")],
                            id="graph_info_container",
                            className="row_container_display"
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
                html.Div([
                    html.P("Sub graph 1:", className="control_label"),
                    dcc.Dropdown(
                                id="sub_graph1_dropdown",
                                options=[{'label': elem, 'value': elem} for elem in all_filter_options],
                                multi=True,
                                value=['depth', 'table'],
                                className="dcc_control"),
                    dcc.RadioItems(
                                id="sub_graph1_radio",
                                options=[
                                    {"label": "Histogram ", "value": "histogram"},
                                    #{"label": "Scatter", "value": "scatter"},
                                    #{"label": "Regression", "value": "regression"},
                                    {"label": "Linear", "value": "linear", },
                                    #{"label": "Pie", "value": "pie"}
                                ],
                                value='histogram',
                                labelStyle={"display": "inline-block"},
                                className="dcc_control",
                            )
                ],
                    className="pretty_container three columns",
                ),
                html.Div([
                    dcc.Graph(id="sub_graph_1", figure={})
                ],
                    className="pretty_container nine columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div([
                    html.P("Sub graph 2:", className="control_label"),
                    dcc.Dropdown(
                        id="sub_graph2_dropdown",
                        options=[{'label': elem, 'value': elem} for elem in all_filter_options],
                        multi=True,
                        value=['carat', 'x'],
                        className="dcc_control"),
                    dcc.RadioItems(
                        id="sub_graph2_radio",
                        options=[
                            {"label": "Histogram ", "value": "histogram"},
                            #{"label": "Scatter", "value": "scatter"},
                            #{"label": "Regression", "value": "regression"},
                            {"label": "Linear", "value": "linear"},
                            #{"label": "Pie", "value": "pie"}
                        ],
                        value='linear',
                        labelStyle={"display": "inline-block"},
                        className="dcc_control",
                    )
                ],
                    className="pretty_container three columns",
                ),
                html.Div(
                    [dcc.Graph(id="sub_graph_2", figure={})
                ],
                    className="pretty_container nine columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

# Callback for main graph
@app.callback(
    Output(component_id='main_graph', component_property='figure'),
    [Input(component_id='table_type', component_property='value'),
     Input(component_id='all_variable_filter', component_property='value')
     ])
def update_main_graph(table_type, all_variable_filter):
    dff = df.copy()
    fig = go.Figure()
    fig.update_layout(plot_bgcolor='#F9F9F9',
                      paper_bgcolor='#F9F9F9', )

    hex_number = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    hex_number = '#' + hex_number

    if table_type == "dataframe":
        dff = dff.head(10)
        fig.add_trace(go.Table(
            header=dict(values=list(dff.columns)),
            cells=dict(values=[dff[elem] for elem in dff.columns])
                              )
                      )
        fig.update_layout(title_text=f'{table_type}')

    elif table_type == "describe":
        dff = dff.describe(include='all')
        dff.insert(loc=0, column='Stats', value=list(dff.index))
        fig.add_trace(go.Table(
            header=dict(values=list(dff.columns)),
            cells=dict(values=[dff[elem] for elem in dff.columns])
                              )
                      )
        fig.update_layout(title_text=f'{table_type}')

    elif table_type == 'uniques':
        for elem in all_variable_filter:
            hex_number = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
            hex_number = '#' + hex_number

            fig.add_trace(go.Histogram(x=dff[f'{elem}'],
                                       marker_color=hex_number,
                                       name=f'{elem}',
                                       opacity=0.75,
                                       nbinsx=20))
            fig.update_layout(title_text='Histogram',
                              plot_bgcolor='#F9F9F9',
                              paper_bgcolor='#F9F9F9',
                              bargap=0.2,
                              bargroupgap=0.1,
                              yaxis=dict(title_text='Count of diamonds',
                                         titlefont=dict(size=20),
                                         range=[0, 15000],
                                         dtick=1500
                                         ),
                              xaxis=dict(title_text=f'{" ".join(all_variable_filter)}',
                                         titlefont=dict(size=20),
                                         )
                              )
            fig.update_layout(title_text=f'Sample distribution in terms of categorical variables')
            fig.update_xaxes(tickangle=45)

    return fig


# Callback for sub graph 1
@app.callback(
    Output(component_id='sub_graph_1', component_property='figure'),
    [Input(component_id='sub_graph1_dropdown', component_property='value'),
     Input(component_id='sub_graph1_radio', component_property='value'),
     Input(component_id='price_slider', component_property='value'),
     Input(component_id='color_selector', component_property='value')])
def update_sub_graph_1(sub_graph1_dropdown, sub_graph1_radio, price_slider, color_selector):

    dff = df.copy()

    if color_selector == 'all':
        dff = dff.loc[dff['price'].isin(range(price_slider[0], price_slider[1]))]
    else:
        dff = dff.loc[(dff['price'].isin(range(price_slider[0], price_slider[1]))) & (df['color'] == color_selector)]

    fig1 = None

    if sub_graph1_radio == 'histogram':
        fig1 = histogram(sub_graph1_dropdown, dff)
    elif sub_graph1_radio == 'linear':
        fig1 = scatter(sub_graph1_dropdown, dff)

    return fig1


# Callback for sub graph 2
@app.callback(
    Output(component_id='sub_graph_2', component_property='figure'),
    [Input(component_id='sub_graph2_dropdown', component_property='value'),
     Input(component_id='sub_graph2_radio', component_property='value'),
     Input(component_id='price_slider', component_property='value'),
     Input(component_id='color_selector', component_property='value')])
def update_sub_graph_2(sub_graph2_dropdown, sub_graph2_radio, price_slider, color_selector):

    dff = df.copy()
    if color_selector == 'all':
        dff = dff.loc[dff['price'].isin(range(price_slider[0], price_slider[1]))]
    else:
        dff = dff.loc[(dff['price'].isin(range(price_slider[0], price_slider[1]))) & (df['color'] == color_selector)]

    fig2 = None
    if sub_graph2_radio == 'histogram':
        fig2 = histogram(sub_graph2_dropdown, dff)
    elif sub_graph2_radio == 'linear':
        fig2 = scatter(sub_graph2_dropdown, dff)
    return fig2


def histogram(columns, dataf):

    figure = go.Figure()

    for elem in columns:
        hex_number = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        hex_number = '#' + hex_number
        figure.add_trace(go.Histogram(x=dataf[f'{elem}'],
                                      marker_color=hex_number,
                                      name=f'{elem}',
                                      opacity=0.75,
                                      nbinsx=20)
                         )
        figure.update_layout(title_text='Histogram',
                             plot_bgcolor='#F9F9F9',
                             paper_bgcolor='#F9F9F9',
                             bargap=0.2,
                             bargroupgap=0.1,
                             yaxis=dict(title_text='Count of diamonds',
                                        titlefont=dict(size=20),
                                        range=[0, 15000],
                                        dtick=1500
                                        ),
                             xaxis=dict(title_text=f'{" ".join(columns)}',
                                        titlefont=dict(size=20),
                                        )
                             )
    figure.update_yaxes(automargin=True)
    return figure


def scatter(columns, dataf):

    figure = go.Figure()

    hex_number = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    hex_number = '#' + hex_number

    for elem in columns:

        df = dataf.groupby(f'{elem}').mean().reset_index()

        figure.add_trace(go.Scattergl(x=df[f'{elem}'],
                                      y=df['price'],
                                      name=f'{elem}'
                                      )
                         )
        figure.update_layout(title_text='Scatter plot',
                             plot_bgcolor='#F9F9F9',
                             paper_bgcolor='#F9F9F9',
                             bargap=0.2,
                             bargroupgap=0.1,
                             yaxis=dict(title_text='Price',
                                        titlefont=dict(size=20),
                                        range=[0, 15000],
                                        dtick=2000,
                                        autorange=True
                                        ),
                             xaxis=dict(title_text=f'{" - ".join(columns)}',
                                        titlefont=dict(size=20),

                                        )
                             )

    return figure


# Main
if __name__ == "__main__":
    webbrowser.open_new_tab('http://127.0.0.1:8050/')
    app.run_server(debug=True, use_reloader=False)

