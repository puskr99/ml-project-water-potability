from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import pickle

# Define page layouts
# prediction_layout = html.Div([
#     html.H1("prediction page"),
#     html.P("Welcome to the home page!")
# ])
prediction_layout = dbc.Container([
    html.H1("Car Price Category Prediction Model", className="text-center mt-4 text-primary fw-bold"),
])