import dash
import pandas as pd
import dash_leaflet as dl
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input


df = pd.read_csv('data/canalwater1.csv')

df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df = df.dropna(subset=["Latitude", "Longitude"])
print("Valid Coordinates Count:", len(df))
df['year'] = df['year'].astype(int) - 543



for param in ['  pH','TEMP. (oC)',  'DO (mg/l)', 'H2S (mg/l)', 'BOD (mg/l)', 'COD (mg/l)', 'SS (mg/l)', 'TKN (mg/l)', 'NH3N (mg/l)', 'NO2 (mg/l)', 'NO3 (mg/l)', 'T-P (mg/l)', 'T.Coliform (col/100ml)']:
    if param in df.columns:
        df[param] = pd.to_numeric(df[param], errors='coerce')


columns_to_exclude = ['BO', 'SS', 'Temp', 'DO', 'ISQA', 'Longitude', 'Latitude']
columns_to_exclude += [col for col in df.columns if 'unnamed' in col.lower()]
df_filtered = df.drop(columns=[col for col in columns_to_exclude if col in df.columns], errors='ignore')

correlation_matrix = df_filtered.corr(numeric_only=True)

canal_options = [{'label': 'All Canals', 'value': 'all'}] + [{'label': canal, 'value': canal} for canal in df['Canal_name (EN)'].unique()]
parameter_options = [
    {'label': 'pH', 'value': '  pH'},
    {'label': 'Temperature (°C)', 'value': 'TEMP. (oC)'},
    {'label': 'Dissolved Oxygen (mg/l)', 'value': 'DO (mg/l)'},
    {'label': 'Hydrogen Sulfide (mg/l)', 'value': 'H2S (mg/l)'},
    {'label': 'Biochemical Oxygen Demand (mg/l)', 'value': 'BOD (mg/l)'},
    {'label': 'Chemical Oxygen Demand (mg/l)', 'value': 'COD (mg/l)'},
    {'label': 'Suspended Solids (mg/l)', 'value': 'SS (mg/l)'},
    {'label': 'Total Kjeldahl Nitrogen (mg/l)', 'value': 'TKN (mg/l)'},
    {'label': 'Ammonia Nitrogen (mg/l)', 'value': 'NH3N (mg/l)'},
    {'label': 'Nitrite[NO2] (mg/l)', 'value': 'NO2 (mg/l)'},
    {'label': 'Nitrate[NO3] (mg/l)', 'value': 'NO3 (mg/l)'},
    {'label': 'Total Phosphorus (mg/l)', 'value': 'T-P (mg/l)'},
    {'label': 'Total Coliform (col/100ml)', 'value': 'T.Coliform (col/100ml)'}
]
year_options = [{'label': 'All Years', 'value': 'all'}] + [{'label': str(year), 'value': str(year)} for year in sorted(df["year"].unique())]

# Define safety thresholds for each parameter
safety_thresholds = {
    '  pH': {'safe': (6.5, 8.5), 'moderate': (5.5, 9.5), 'unsafe': (-float('inf'), float('inf'))},
    'TEMP. (oC)': {'safe': (15, 30), 'moderate': (10, 35), 'unsafe': (-float('inf'), float('inf'))},
    'DO (mg/l)': {'safe': (5, 8), 'moderate': (3, 10), 'unsafe': (-float('inf'), float('inf'))},
    'H2S (mg/l)': {'safe': (0, 0.05), 'moderate': (0.05, 0.1), 'unsafe': (0.1, float('inf'))},
    'BOD (mg/l)': {'safe': (0, 2), 'moderate': (2, 5), 'unsafe': (5, float('inf'))},
    'COD (mg/l)': {'safe': (0, 15), 'moderate': (15, 30), 'unsafe': (30, float('inf'))},
    'SS (mg/l)': {'safe': (0, 10), 'moderate': (10, 30), 'unsafe': (30, float('inf'))},
    'TKN (mg/l)': {'safe': (0, 1), 'moderate': (1, 3), 'unsafe': (3, float('inf'))},
    'NH3N (mg/l)': {'safe': (0, 0.5), 'moderate': (0.5, 1.5), 'unsafe': (1.5, float('inf'))},
    'NO2 (mg/l)': {'safe': (0, 0.1), 'moderate': (0.1, 0.5), 'unsafe': (0.5, float('inf'))},
    'NO3 (mg/l)': {'safe': (0, 10), 'moderate': (10, 50), 'unsafe': (50, float('inf'))},
    'T-P (mg/l)': {'safe': (0, 0.2), 'moderate': (0.2, 1.0), 'unsafe': (1.0, float('inf'))},
    'T.Coliform (col/100ml)': {'safe': (0, 1000), 'moderate': (1000, 100000), 'unsafe': (100000, float('inf'))}
}

# Function to determine safety status and color
def get_safety_status(value, parameter):
    if pd.isna(value) or not isinstance(value, (int, float)):
        print(f"Invalid value for {parameter}: {value}")
        return 'unknown', '#808080'  # Gray
    thresholds = safety_thresholds.get(parameter, {'safe': (0, float('inf')), 'moderate': (0, float('inf')), 'unsafe': (0, float('inf'))})
    
    safe_min, safe_max = thresholds['safe']
    moderate_min, moderate_max = thresholds['moderate']
    
    if safe_min <= value <= safe_max:
        status = 'safe'
        color = '#00FF00'  # Green
    elif moderate_min <= value <= moderate_max:
        status = 'moderate'
        color = '#FFFF00'  # Yellow
    else:
        status = 'unsafe'
        color = '#FF0000'  # Red
    
    # print(f"Parameter: {parameter}, Value: {value}, Status: {status}, Color: {color}")
    return status, color

# Define page layouts
map_layout = dbc.Container([

    # Controls: Dropdowns
    dbc.Row([
        dbc.Col([
            html.Label("Select Canal:", className="fw-semibold"),
            dcc.Dropdown(
                id='canal-dropdown',
                options=canal_options,
                value='all',
                clearable=False,
                className="mb-3"
            ),
        ], md=4),  

        dbc.Col([
            html.Label("Select Parameter:", className="fw-semibold"),
            dcc.Dropdown(
                id='parameter-dropdown',
                options=parameter_options,
                value='  pH',
                clearable=False,
                className="mb-3"
            ),
        ], md=4),

        dbc.Col([
            html.Label("Select Year:", className="fw-semibold"),
            dcc.Dropdown(
                id='year-dropdown',
                options=year_options,
                value='all',
                clearable=False,
                className="mb-3"
            ),
        ], md=4),
    ], className="mb-4"),


    # Map full-width
    dbc.Row([
        dbc.Col(
            dl.Map(
                id='map',
                center=[13.7563, 100.5018],
                zoom=10,
                children=[
                    dl.TileLayer(
                        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                        attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>',
                        subdomains='abcd',
                        maxZoom=20
                    ),
                    dl.LayerGroup(id='marker-layer')
                ],
                style={'width': '100%', 'height': '600px'}
            ),
            md=12
        )
    ])
], fluid=True,style={'paddingBottom': '40px'})

prediction_layout = dbc.Container([
    html.H1("Water Quality Prediction Model", className="text-center mt-4 text-primary fw-bold"),
])

# Callback to update map
@callback(
    Output("marker-layer", "children"),
    [Input("canal-dropdown", "value"),
     Input("parameter-dropdown", "value"),
     Input("year-dropdown", "value")]
)
def update_map_markers(selected_canal, selected_parameter, selected_year):
    if selected_canal == 'all':
        filtered_df = df if selected_year == 'all' else df[df['year'] == int(selected_year)]
    else:
        filtered_df = df[(df['Canal_name (EN)'] == selected_canal) & (df['year'] == int(selected_year))] if selected_year != 'all' else df[df['Canal_name (EN)'] == selected_canal]
    
    markers = []
    for idx, row in filtered_df.iterrows():
        if pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):
            status, color = get_safety_status(row[selected_parameter], selected_parameter)
            # Map status to Google Maps pin image
            pin_image = {
                'safe': 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'moderate': 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                'unsafe': 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
                'unknown': 'https://maps.google.com/mapfiles/ms/icons/grey-dot.png'
            }[status]
            marker = dl.Marker(
                position=[row["Latitude"], row["Longitude"]],
                icon={
                    "iconUrl": pin_image,
                    "iconSize": [32, 32],  # Adjust size to match Google Maps pin
                    "iconAnchor": [16, 32],  # Anchor at pin's point
                    "popupAnchor": [0, -32]
                },
                children=[
                    dl.Tooltip(html.Div([
                        html.Div(f"Canal: {row['Canal_name (EN)']}"),
                        html.Div(f"Sampling Point: {row['Sample_water_point (EN)']}"),
                        html.Div(f"{selected_parameter}: {row[selected_parameter]} ({status})")
                    ]))
                ]
            )
            markers.append(marker)
    
    print(f"Map updated with {len(markers)} markers for {'All Canals' if selected_canal == 'all' else selected_canal}, {'All Years' if selected_year == 'all' else selected_year}")
    return markers

# @callback(
#     Output("page-content", "children"),
#     Input("url", "pathname")
# )
# def render_page_content(pathname):
#     if pathname == "/prediction":
#         return prediction_layout
#     else:
#         return map_layout

__all__ = ['map_layout']
