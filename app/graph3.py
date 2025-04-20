# import dash
# import dash_bootstrap_components as dbc
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import pandas as pd
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import warnings
# warnings.filterwarnings("ignore")

# # Load the dataset
# df = pd.read_csv('data/water.csv')

# # Clean the data
# df = df.dropna(subset=['year', 'Canal_name (EN)', 'Sample_water_point (EN)', '  pH', 'SS (mg/l)', 'NH3N (mg/l)', 'DO (mg/l)', 'TEMP. (oC)', 'H2S (mg/l)', 'BOD (mg/l)', 'COD (mg/l)', 'TKN (mg/l)', 'NO2 (mg/l)', 'NO3 (mg/l)', 'T-P (mg/l)', 'T.Coliform (col/100ml)'])
# df = df[df['Canal_name (EN)'] != '#VALUE!']
# df['year'] = df['year'].astype(int) - 543

# # Aggregate data
# aggregated_df = df.groupby(['Canal_name (EN)', 'year']).agg({
#     '  pH': 'mean',
#     'DO (mg/l)': 'mean',
#     'SS (mg/l)': 'mean',
#     'NH3N (mg/l)': 'mean',
#     'TEMP. (oC)': 'mean',
#     'H2S (mg/l)': 'mean',
#     'BOD (mg/l)': 'mean',
#     'COD (mg/l)': 'mean',
#     'TKN (mg/l)': 'mean',
#     'NO2 (mg/l)': 'mean',
#     'NO3 (mg/l)': 'mean',
#     'T-P (mg/l)': 'mean',
#     'T.Coliform (col/100ml)': 'mean',
# }).reset_index()

# # Dropdown options
# canal_options = [{'label': canal, 'value': canal} for canal in aggregated_df['Canal_name (EN)'].unique()]
# year_options = [{'label': str(year), 'value': year} for year in sorted(aggregated_df['year'].unique())]

# # Dash app
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap"])

# app.layout = dbc.Container([
#     html.H1("Water Quality Dashboard", className="text-center mt-4 mb-2", style={"fontFamily": "Inter, sans-serif"}),

#     dbc.Row([
#         dbc.Col([
#             html.Label("Select Year:"),
#             dcc.Dropdown(id='year-dropdown', options=year_options, value=year_options[0]['value'], clearable=False),
#             html.Label("Select Canal:", style={"marginTop": "20px"}),
#             dcc.Dropdown(id='canal-dropdown', options=canal_options, value=canal_options[0]['value'], clearable=False),
#         ], md=4),
#     ]),

#     dbc.Row([
#         dbc.Col([
#             dcc.Graph(id='gauge-graph')
#         ], md=12)
#     ])
# ], fluid=True)

# # Callback for updating gauges
# @app.callback(
#     Output('gauge-graph', 'figure'),
#     Input('year-dropdown', 'value'),
#     Input('canal-dropdown', 'value')
# )
# def update_gauge_graph(selected_year, selected_canal):
#     filtered_df = aggregated_df[(aggregated_df['year'] == selected_year) & 
#                                 (aggregated_df['Canal_name (EN)'] == selected_canal)]
#     if filtered_df.empty:
#         return go.Figure()

#     # Extract values
#     metrics = filtered_df.iloc[0]
#     values = {
#         'pH': metrics['  pH'],
#         'DO': metrics['DO (mg/l)'],
#         'TDS': metrics['SS (mg/l)'],
#         'NH3N': metrics['NH3N (mg/l)'],
#         'TEMP': metrics['TEMP. (oC)'],
#         'H2S': metrics['H2S (mg/l)'],
#         'BOD': metrics['BOD (mg/l)'],
#         'COD': metrics['COD (mg/l)'],
#         'TKN': metrics['TKN (mg/l)'],
#         'NO2': metrics['NO2 (mg/l)'],
#         'NO3': metrics['NO3 (mg/l)'],
#         'TP': metrics['T-P (mg/l)'],
#         'TC': metrics['T.Coliform (col/100ml)']
#     }

#     thresholds = {
#         'pH': [6.5, 8.5], 'DO': [2, 6], 'TDS': [50, 100], 'NH3N': [1.5, 5], 'TEMP': [30, 40],
#         'H2S': [0.05, 0.1], 'BOD': [2, 5], 'COD': [20, 50], 'TKN': [1, 5], 'NO2': [0.05, 0.1],
#         'NO3': [5, 10], 'TP': [0.2, 0.5], 'TC': [1000, 3000]
#     }

#     max_ranges = {
#         'pH': 14, 'DO': 10, 'TDS': 200, 'NH3N': 15, 'TEMP': 50,
#         'H2S': 1, 'BOD': 50, 'COD': 100, 'TKN': 20, 'NO2': 1,
#         'NO3': 20, 'TP': 2, 'TC': 5000
#     }

#     fig = make_subplots(rows=3, cols=5, specs=[[{'type': 'indicator'}]*5]*3)
#     row, col = 1, 1

#     for i, (name, val) in enumerate(values.items()):
#         limit1, limit2 = thresholds[name]
#         fig.add_trace(go.Indicator(
#             mode="gauge+number",
#             value=val,
#             title={'text': name},
#             gauge={
#                 'axis': {'range': [0, max_ranges[name]], 'tickwidth': 1, 'tickcolor': "#7f8c8d"},
#                 'bar': {'color': "#2c3e50"},
#                 'steps': [
#                     {'range': [0, limit1], 'color': "#00C49F"},
#                     {'range': [limit1, limit2], 'color': "#FFD700"},
#                     {'range': [limit2, max_ranges[name]], 'color': "#FF6B6B"}
#                 ],
#                 'threshold': {
#                     'line': {'color': "blue", 'width': 4},
#                     'thickness': 0.75,
#                     'value': limit2
#                 }
#             }
#         ), row=row, col=col)
#         col += 1
#         if col > 5:
#             row += 1
#             col = 1

#     fig.update_layout(
#         template='plotly_white',
#         font=dict(family="Inter, sans-serif", size=14, color="#333"),
#         title_text=f"Water Quality Metrics – {selected_canal} ({selected_year})",
#         title_x=0.5,
#         height=900,
#         margin=dict(t=60, b=40, l=40, r=40)
#     )
#     return fig

# # Run
# if __name__ == '__main__':
#     app.run(debug=True)

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# Load the dataset
df = pd.read_csv('data/water.csv')
df = df.dropna(subset=['year', 'Canal_name (EN)', 'Sample_water_point (EN)', '  pH', 'SS (mg/l)', 'NH3N (mg/l)', 'DO (mg/l)', 'TEMP. (oC)', 'H2S (mg/l)', 'BOD (mg/l)', 'COD (mg/l)', 'TKN (mg/l)', 'NO2 (mg/l)', 'NO3 (mg/l)', 'T-P (mg/l)', 'T.Coliform (col/100ml)'])
df = df[df['Canal_name (EN)'] != '#VALUE!']
df['year'] = df['year'].astype(int) - 543

aggregated_df = df.groupby(['Canal_name (EN)', 'year']).agg({
    '  pH': 'mean', 'DO (mg/l)': 'mean', 'SS (mg/l)': 'mean', 'NH3N (mg/l)': 'mean',
    'TEMP. (oC)': 'mean', 'H2S (mg/l)': 'mean', 'BOD (mg/l)': 'mean', 'COD (mg/l)': 'mean',
    'TKN (mg/l)': 'mean', 'NO2 (mg/l)': 'mean', 'NO3 (mg/l)': 'mean', 'T-P (mg/l)': 'mean',
    'T.Coliform (col/100ml)': 'mean',
}).reset_index()

canal_options = [{'label': canal, 'value': canal} for canal in aggregated_df['Canal_name (EN)'].unique()]
year_options = [{'label': str(year), 'value': year} for year in sorted(aggregated_df['year'].unique())]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap"])
app.title = "Bangkok Water Dashboard"

navbar = dbc.NavbarSimple(
    brand="Bangkok Water Quality",
    brand_href="/",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Prediction", href="/prediction")),
    ]
)

home_layout = dbc.Container([
    html.H2("Dashboard Overview", className="mt-4 mb-2", style={"fontFamily": "Inter, sans-serif"}),
    html.P([
        "Bangkok canals serve as transportation routes, provide water for domestic and industrial use, and support the local economy. ",
        "For our water quality prediction, we have utilized a dataset sourced from Bangkok’s water canals, available at: ",
        html.A("Link", href="https://data.bangkok.go.th/sv/dataset/kpisbangkok_3101/resource/61d86d7e-a765-41cc-9cbd-ff0006bec752", target="_blank", style={'color': '#007bff', 'textDecoration': 'underline'}),
        ". This dataset includes key metrics such as Suspended Solids (SS, approximating Total Dissolved Solids), pH, Ammonia (NH3N), Dissolved Oxygen (DO), and Temperature, capturing the environmental conditions of these water bodies at various sampling points over 3 years (2018-2020)."
    ], style={"fontSize": "15px", "color": "#333"}),

    dbc.Row([
        dbc.Col([
            html.Label("Select Year:"),
            dcc.Dropdown(id='year-dropdown', options=year_options, value=year_options[0]['value'], clearable=False),
            html.Label("Select Canal:", style={"marginTop": "20px"}),
            dcc.Dropdown(id='canal-dropdown', options=canal_options, value=canal_options[0]['value'], clearable=False),
        ], md=4),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='gauge-graph')
        ], md=12)
    ])
], fluid=True)

prediction_layout = dbc.Container([
    html.H2("Prediction Page Coming Soon...", className="text-center mt-4")
], fluid=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/prediction':
        return prediction_layout
    return home_layout

@app.callback(
    Output('gauge-graph', 'figure'),
    Input('year-dropdown', 'value'),
    Input('canal-dropdown', 'value')
)
def update_gauge_graph(selected_year, selected_canal):
    filtered_df = aggregated_df[(aggregated_df['year'] == selected_year) & 
                                (aggregated_df['Canal_name (EN)'] == selected_canal)]
    if filtered_df.empty:
        return go.Figure()

    metrics = filtered_df.iloc[0]
    values = {
        'pH': metrics['  pH'], 'DO': metrics['DO (mg/l)'], 'TDS': metrics['SS (mg/l)'],
        'NH3N': metrics['NH3N (mg/l)'], 'TEMP': metrics['TEMP. (oC)'], 'H2S': metrics['H2S (mg/l)'],
        'BOD': metrics['BOD (mg/l)'], 'COD': metrics['COD (mg/l)'], 'TKN': metrics['TKN (mg/l)'],
        'NO2': metrics['NO2 (mg/l)'], 'NO3': metrics['NO3 (mg/l)'], 'TP': metrics['T-P (mg/l)'],
        'TC': metrics['T.Coliform (col/100ml)']
    }

    thresholds = {
        'pH': [6.5, 8.5], 'DO': [2, 6], 'TDS': [50, 100], 'NH3N': [1.5, 5], 'TEMP': [30, 40],
        'H2S': [0.05, 0.1], 'BOD': [2, 5], 'COD': [20, 50], 'TKN': [1, 5], 'NO2': [0.05, 0.1],
        'NO3': [5, 10], 'TP': [0.2, 0.5], 'TC': [1000, 3000]
    }

    max_ranges = {
        'pH': 14, 'DO': 10, 'TDS': 200, 'NH3N': 15, 'TEMP': 50,
        'H2S': 1, 'BOD': 50, 'COD': 100, 'TKN': 20, 'NO2': 1,
        'NO3': 20, 'TP': 2, 'TC': 5000
    }

    fig = make_subplots(rows=3, cols=5, specs=[[{'type': 'indicator'}]*5]*3)
    row, col = 1, 1

    for i, (name, val) in enumerate(values.items()):
        limit1, limit2 = thresholds[name]
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=val,
            title={'text': name},
            gauge={
                'axis': {'range': [0, max_ranges[name]], 'tickwidth': 1, 'tickcolor': "#7f8c8d"},
                'bar': {'color': "#2c3e50"},
                'steps': [
                    {'range': [0, limit1], 'color': "#00C49F"},
                    {'range': [limit1, limit2], 'color': "#FFD700"},
                    {'range': [limit2, max_ranges[name]], 'color': "#FF6B6B"}
                ],
                'threshold': {
                    'line': {'color': "blue", 'width': 4},
                    'thickness': 0.75,
                    'value': limit2
                }
            }
        ), row=row, col=col)
        col += 1
        if col > 5:
            row += 1
            col = 1

    fig.update_layout(
        template='plotly_white',
        font=dict(family="Inter, sans-serif", size=14, color="#333"),
        title_text=f"Water Quality Metrics – {selected_canal} ({selected_year})",
        title_x=0.5,
        height=900,
        margin=dict(t=60, b=40, l=40, r=40)
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)