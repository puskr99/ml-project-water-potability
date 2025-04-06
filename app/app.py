import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
# from home import home_layout
# from prediction import prediction_layout

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

# Initializ the dash app ; suppress_callback_exceptions: allow for the ids to be added later.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Thailand cannal water Prediction"

# Define the navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Prediction", href="/prediction")),
    ],
    brand="Water Quality Prediction",
    brand_href="/",
    color="primary",
    dark=True,
)

df = pd.read_csv('data/water.csv')

canal_options = [{'label': canal, 'value': canal} for canal in df['Canal_name (EN)'].unique()]

# Water quality parameters for dropdown
parameter_options = [
    {'label': 'Temperature (°C)', 'value': 'TEMP. (oC)'},
    {'label': '  pH', 'value': '  pH'},
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

# Define page layouts
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
                            value='TEMP. (oC)',  # Default to pH
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

prediction_layout = dbc.Container([
    html.H1("Car Price Category Prediction Model", className="text-center mt-4 text-primary fw-bold"),
])

# page1_layout = html.Div([
#     html.H1("Page 1"),
#     html.P("This is page 1 content")
# ])

# page2_layout = html.Div([
#     html.H1("Page 2"),
#     html.P("This is page 2 content")
# ])

# about_layout = html.Div([
#     html.H1("About"),
#     html.P("This is the about page")
# ])




# App layout with URL routing
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    html.Div(id="page-content")
])

# Callback to update page content based on URL
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)

def display_page(pathname):
    if pathname == '/prediction':
        return prediction_layout
    else:
        return home_layout
    

# def display_page(pathname):
#     if pathname == "/page-1":
#         return page1_layout
#     elif pathname == "/page-2":
#         return page2_layout
#     elif pathname == "/about":
#         return about_layout
#     else:
#         return home_layout

@app.callback(
    Output('water-quality-graph', 'figure'),
    [Input('canal-dropdown', 'value'),
     Input('parameter-dropdown', 'value')]
)
def update_graph(selected_canal, selected_parameter):
    # Filter data by selected canal
    filtered_df = df[df['Canal_name (EN)'] == selected_canal]
    
    # Create bar chart
    fig = {
        'data': [
            {
                'x': filtered_df['Sample_water_point (EN)'],
                'y': filtered_df[selected_parameter],
                'type': 'bar',
                'name': selected_parameter,
                'marker': {'color': '#007bff'}  # Optional: Add color for better visuals
            }
        ],
        'layout': {
            'title': f'{selected_parameter} in {selected_canal}',
            'xaxis': {
                # 'title': 'Sampling Point',
                'title': {
                    'text': 'Sampling Points',  # X-axis title
                    'font': {
                        'size': 14,
                        'color': '#333'
                    }
                },
                'tickangle': -45,  # Rotate labels for readability
                'automargin': True
            },
            'yaxis': {
                'title': {
                    'text': f'{selected_parameter}',  # Y-axis title
                    'font': {
                        'size': 14,
                        'color': '#333'
                    }
                }
            },
            'margin': {'b': 150},  # Adjust bottom margin for rotated labels
            'plot_bgcolor': '#f8f9fa',  # Light background
            'paper_bgcolor': '#f8f9fa'
        }
    }
    return fig


# Run the app
if __name__ == "__main__":
    app.run(debug=True)