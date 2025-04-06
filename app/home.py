from dash import html, dcc, Output, Input, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
# from app import app  # Import app for callback registration

# Define page layouts
# home_layout = html.Div([
#     html.H1("Home Page"),
#     html.P("Welcome to the home page!")
# ])

df = pd.read_csv('data/water.csv')

canal_options = [{'label': canal, 'value': canal} for canal in df['Canal_name (EN)'].unique()]

# Water quality parameters for dropdown
parameter_options = [
    {'label': 'Temperature (°C)', 'value': 'TEMP. (oC)'},
    {'label': 'pH', 'value': 'pH'},
    {'label': 'Dissolved Oxygen (mg/l)', 'value': 'DO (mg/l)'},
    {'label': 'Hydrogen Sulfide (mg/l)', 'value': 'H2S (mg/l)'},
    {'label': 'Biochemical Oxygen Demand (mg/l)', 'value': 'BOD (mg/l)'},
    {'label': 'Chemical Oxygen Demand (mg/l)', 'value': 'COD (mg/l)'},
    {'label': 'Suspended Solids (mg/l)', 'value': 'SS (mg/l)'},
    {'label': 'Total Kjeldahl Nitrogen (mg/l)', 'value': 'TKN (mg/l)'},
    {'label': 'Ammonia Nitrogen (mg/l)', 'value': 'NH3N (mg/l)'},
    {'label': 'Nitrite (mg/l)', 'value': 'NO2 (mg/l)'},
    {'label': 'Nitrate (mg/l)', 'value': 'NO3 (mg/l)'},
    {'label': 'Total Phosphorus (mg/l)', 'value': 'T-P (mg/l)'},
    {'label': 'Total Coliform (col/100ml)', 'value': 'T.Coliform (col/100ml)'}
]


home_layout = dbc.Container(
    [
        html.H1("Water Quality Dashboard"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select Canal:"),
                        dcc.Dropdown(
                            id='canal-dropdown',
                            options=canal_options,
                            value=canal_options[0]['value'],  # Default to first canal
                            clearable=False
                        ),
                        html.Label("Select Parameter:", style={'marginTop': '20px'}),
                        dcc.Dropdown(
                            id='parameter-dropdown',
                            options=parameter_options,
                            value='pH',  # Default to pH
                            clearable=False
                        ),
                    ],
                    md=4
                ),
                dbc.Col(
                    dcc.Graph(id='water-quality-graph'),
                    md=8
                ),
            ],
            align="center",
        ),
    ],
    fluid=True,
)

# Callback to update the graph based on dropdown selections
# @app.callback(
#     Output('water-quality-graph', 'figure'),
#     [Input('canal-dropdown', 'value'),
#      Input('parameter-dropdown', 'value')]
# )
# def update_graph(selected_canal, selected_parameter):
#     # Filter data by selected canal
#     filtered_df = df[df['Canal_name (EN)'] == selected_canal]
    
#     # Create bar chart
#     fig = {
#         'data': [
#             {
#                 'x': filtered_df['Sample_water_point (EN)'],
#                 'y': filtered_df[selected_parameter],
#                 'type': 'bar',
#                 'name': selected_parameter,
#                 'marker': {'color': '#007bff'}  # Optional: Add color for better visuals
#             }
#         ],
#         'layout': {
#             'title': f'{selected_parameter} in {selected_canal}',
#             'xaxis': {
#                 'title': 'Sampling Point',
#                 'tickangle': -45,  # Rotate labels for readability
#                 'automargin': True
#             },
#             'yaxis': {'title': selected_parameter},
#             'margin': {'b': 150},  # Adjust bottom margin for rotated labels
#             'plot_bgcolor': '#f8f9fa',  # Light background
#             'paper_bgcolor': '#f8f9fa'
#         }
#     }
#     return fig