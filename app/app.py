import dash
import numpy as np
import pandas as pd
import dash_leaflet as dl
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
from dash import dcc, html, Input, Output, State, no_update

from map import map_layout

import os
import warnings
warnings.filterwarnings("ignore")

import joblib
model = joblib.load("code/wpp_model_weight.pkl")
scaler = joblib.load("code/scaler.dump")

df = pd.read_csv('data/water.csv')
df = df.dropna(subset=['year', 'Canal_name (EN)', 'Sample_water_point (EN)', '  pH', 'SS (mg/l)', 'NH3N (mg/l)', 'DO (mg/l)', 'TEMP. (oC)', 'H2S (mg/l)', 'BOD (mg/l)', 'COD (mg/l)', 'TKN (mg/l)', 'NO2 (mg/l)', 'NO3 (mg/l)', 'T-P (mg/l)', 'T.Coliform (col/100ml)'])
df = df[df['Canal_name (EN)'] != '#VALUE!']
df['year'] = df['year'].astype(int) - 543

map_df = pd.read_csv('data/canalwater1.csv')

map_df = map_df[['Canal_name (EN)', 'Latitude', 'Longitude', '  pH', 'DO (mg/l)', 'SS (mg/l)']]
map_df = map_df.dropna(subset=['Latitude', 'Longitude', '  pH', 'DO (mg/l)', 'SS (mg/l)'])
map_df = map_df[(map_df['Latitude'] != 0) & (map_df['Longitude'] != 0)]

aggregated_df = df.groupby(['Canal_name (EN)', 'year']).agg({
    '  pH': 'mean', 'DO (mg/l)': 'mean', 'SS (mg/l)': 'mean', 'NH3N (mg/l)': 'mean',
    'TEMP. (oC)': 'mean', 'H2S (mg/l)': 'mean', 'BOD (mg/l)': 'mean', 'COD (mg/l)': 'mean',
    'TKN (mg/l)': 'mean', 'NO2 (mg/l)': 'mean', 'NO3 (mg/l)': 'mean', 'T-P (mg/l)': 'mean',
    'T.Coliform (col/100ml)': 'mean',
}).reset_index()

canal_options = [{'label': canal, 'value': canal} for canal in df['Canal_name (EN)'].unique() if canal != '#VALUE!']
year_options = [{'label': str(year), 'value': year} for year in sorted(df['year'].unique())]

feature_info = {
    "ph": ("  pH", "pH"),
    "do": ("DO (mg/l)", "Dissolved Oxygen (mg/l)"),
    "tds": ("SS (mg/l)", "Suspended Solids (mg/l)"),
    "nh3n": ("NH3N (mg/l)", "Ammonia (mg/l)"),
    "temp": ("TEMP. (oC)", "Temperature (oC)"),
    "h2s": ("H2S (mg/l)", "Hydrogen Sulfide (mg/l)"),
    "bod": ("BOD (mg/l)", "Biochemical Oxygen Demand (mg/l)"),
    "cod": ("COD (mg/l)", "Chemical Oxygen Demand (mg/l)"),
    "tkn": ("TKN (mg/l)", "Total Kjeldahl Nitrogen (mg/l)"),
    "no2": ("NO2 (mg/l)", "Nitrite (mg/l)"),
    "no3": ("NO3 (mg/l)", "Nitrate (mg/l)"),
    "tp": ("T-P (mg/l)", "Total Phosphorus"),
    "coliform": ("T.Coliform (col/100ml)", "Coliform")
}
selected_feature_keys = ["ph", "do", "bod", "no3", "tds", "cod", "coliform"]

parameter_options = [
    {'label': 'Temperature (°C)', 'value': 'TEMP. (oC)'},
    {'label': 'pH', 'value': '  pH'},
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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Bangkok Canal Water Quality"

navbar = html.Div([
    dcc.Location(id='nav-url', refresh=False),
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("Bangkok Canal Water Quality", href="/", className="fw-semibold fs-4 text-white"),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                html.Div(id="nav-links", className="ms-auto d-flex gap-3"),
                id="navbar-collapse",
                navbar=True,
                is_open=True
            )
        ]),
        color="dark",
        className="border-bottom shadow-sm py-3"
    )
])

# Layouts for Dashboard and Prediction Pages
def dashboard_layout():
    return dbc.Container([
        dcc.Tabs(id="tabs", value='tab-map', children=[
            dcc.Tab(label='Map View', value='tab-map'),
            dcc.Tab(label='Gauge Graph', value='tab-main-graph'),
            dcc.Tab(label='By Canal', value='tab-canal'),
            dcc.Tab(label='Trends', value='tab-trends'),
        ], colors={
            "border": "white",
            "primary": "black",
            "background": "#f7f7f7"
        }),

        html.Div(id='tabs-content', className='mt-4')
    ], fluid=False)

def prediction_layout():
    feature_defaults = {
        "ph": 7.0,
        "do": 6.5,
        "bod": 2.0,
        "no3": 5.0,
        "tds": 300,
        "cod": 20,
        "coliform": 500
    }
    filtered_feature_info = {k: feature_info[k] for k in selected_feature_keys}
    input_fields = list(filtered_feature_info.items())
    cols = [input_fields[i::2] for i in range(2)]

    return dbc.Container([
        html.H2("Water Quality Prediction", className="text-center mt-4 mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Label(info[1]),
                        dbc.Input(
                            type="number",
                            id=key,
                            placeholder=f"Enter {info[1]}",
                            step="any",
                            min=0,
                            value=feature_defaults.get(key, 0),
                            required=True
                        )
                    ], md=6, className="mb-3")
                    for group in cols for key, info in group
                ]),
                html.Div(className="text-center mt-3", children=[
                    dbc.Button("Predict", id="predict-button", color="primary", className="me-2"),
                    dbc.Button("Reset", id="reset-button", color="secondary", className="ms-2")
                ])
                #dbc.Alert(id="prediction-output", color="info", className="mt-4")
            ], md=6),
            dbc.Col([
                dcc.Loading(
                    id="loading-gauge",
                    type="circle",
                    color="#0d6efd",
                    children=[
                        dcc.Graph(id="gauge-graph"),
                        html.Div(id="gauge-label", className="text-center fw-bold fs-4 mt-2")
                ]
                )
            ], md=6),
        ])
    ], fluid=False)

@app.callback(
    Output('gauge-graph', 'figure'),
    Output('gauge-label', 'children'),  
    #Output('prediction-output', 'children'),
    Input('predict-button', 'n_clicks'),
    [State(key, 'value') for key in selected_feature_keys],
    prevent_initial_call=True
)
def predict_quality(n_clicks, *inputs):
    if not n_clicks:
        return no_update, no_update

    if any(val is None for val in inputs):
        return "⚠️ Please fill in all fields before predicting.", no_update

    try:
        values = [float(x) for x in inputs]
        values = np.array(values).reshape(1, -1)
        scaled_data = scaler.transform(values)
        wqi = np.exp(model.predict(scaled_data)[0])

        if wqi >= 75:
            label = "✅ Safe"
            color = "#2c3e50"
        elif wqi >= 50:
            label = "⚠️ Potentially Unsafe"
            color = "#2c3e50"
        else:
            label = "❌ Unsafe"
            color = "#2c3e50"

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=wqi,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Predicted Water Quality Index"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 50], 'color': "#FF6B6B"},
                    {'range': [50, 75], 'color': "#FFD700"},
                    {'range': [75, 100], 'color': "#00C49F"}
                ]
            }
        ))

        return fig, label

    except Exception as e:
        return f"Error in prediction: {e}"


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

# Routing callback
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/prediction':
        return prediction_layout()
    return dashboard_layout()


# Reset button logic
@app.callback(
    [Output(key, 'value') for key in selected_feature_keys],
    Input('reset-button', 'n_clicks')
)
def reset_fields(n):
    if not n:
        return dash.no_update
    return [None] * len(selected_feature_keys)

# App layout with routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

# Dashboard tab content callback
@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_tab_content(tab):
    if tab == 'tab-canal':
        return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Label("Select Canal:", className="fw-bold"),
                dcc.Dropdown(
                    id='bar-canal-dropdown',
                    options=canal_options,
                    value=canal_options[0]['value'],
                    clearable=False
                )
            ], md=6),

            dbc.Col([
                html.Label("Select Metric:", className="fw-bold"),
                dcc.Dropdown(
                    id='bar-metric-dropdown',
                    options=parameter_options,
                    value='DO (mg/l)',
                    clearable=False
                )
            ], md=6)
        ], className="mb-4"),

        dcc.Graph(id='canal-bar-graph')
    ])

    elif tab == 'tab-main-graph':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Year:", className="fw-semibold"),
                    dcc.Dropdown(
                        id='year-dropdown',
                        options=year_options,
                        value=year_options[0]['value'],
                        clearable=False
                    )
                ], xs=6),

                dbc.Col([
                    html.Label("Select Canal:", className="fw-semibold"),
                    dcc.Dropdown(
                        id='canal-dropdown',
                        options=canal_options,
                        value=canal_options[0]['value'],
                        clearable=False
                    )
                ], xs=6)
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='gauge-graph')
                ])
            ])
        ])
    elif tab == 'tab-trends':
        return html.Div([
            html.Label("Select Canal:"),
            dcc.Dropdown(
                id='trend-canal-dropdown',
                options=canal_options,
                value=canal_options[0]['value'],
                clearable=False,
                style={"marginBottom": "20px"}
            ),
            dcc.Graph(id='trend-line-chart')
        ])
    elif tab == 'tab-map':
        return map_layout
       

@app.callback(
    Output('canal-bar-graph', 'figure'),
    Input('bar-canal-dropdown', 'value'),
    Input('bar-metric-dropdown', 'value')
)
def update_bar_chart(selected_canal, selected_metric):
    df_canal = df[df['Canal_name (EN)'] == selected_canal]
    df_grouped = df_canal.groupby('Sample_water_point (EN)')[selected_metric].mean().reset_index()
    fig = px.bar(df_grouped, x='Sample_water_point (EN)', y=selected_metric,
                 title=f"{selected_metric} per Sample Point in {selected_canal}",
                 labels={selected_metric: selected_metric, 'Sample_water_point (EN)': 'Sample Point'},
                 color=selected_metric, height=500, color_continuous_scale='mint')
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500
    )
    return fig

@app.callback(
    Output('gauge-graph', 'figure', allow_duplicate=True),
    Input('year-dropdown', 'value'),
    Input('canal-dropdown', 'value'),
    prevent_initial_call="initial_duplicate"
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

@app.callback(
    Output('card-ph', 'children'),
    Output('card-do', 'children'),
    Output('card-tds', 'children'),
    Input('year-dropdown', 'value'),
    Input('canal-dropdown', 'value')
)
def update_cards(year, canal):
    filtered = aggregated_df[(aggregated_df['year'] == year) & (aggregated_df['Canal_name (EN)'] == canal)]
    if filtered.empty:
        return "N/A", "N/A", "N/A"

    row = filtered.iloc[0]
    return (
        f"{row['  pH']:.2f}",
        f"{row['DO (mg/l)']:.2f}",
        f"{row['SS (mg/l)']:.2f}"
    )

if __name__ == '__main__':
    def update_cards(year, canal):
        filtered = aggregated_df[(aggregated_df['year'] == year) & (aggregated_df['Canal_name (EN)'] == canal)]
        if filtered.empty:
            return "N/A", "N/A", "N/A"

        row = filtered.iloc[0]
        return (
            f"{row['  pH']:.2f}",
            f"{row['DO (mg/l)']:.2f}",
            f"{row['SS (mg/l)']:.2f}"
        )

@app.callback(
    Output('trend-line-chart', 'figure'),
    Input('trend-canal-dropdown', 'value')
)
def update_trend_chart(selected_canal):
    value_vars = [param["value"] for param in parameter_options if param['value'] != 'T.Coliform (col/100ml)']
    df_trend = aggregated_df[aggregated_df['Canal_name (EN)'] == selected_canal].copy()
    df_trend['year'] = df_trend['year'].astype(int)

    # Melt the dataframe to long format
    df_long = df_trend.melt(
        id_vars='year',
        value_vars=value_vars,
        var_name='Metric',
        value_name='Measurement'
    )

    fig = px.line(
        df_long,
        x='year',
        y='Measurement',
        color='Metric',
        markers=True,
        title=f"Water Quality Trends in {selected_canal} (2018–2020)"
    )

    fig.update_layout(
        legend_title_text='Metric',
        height=500,
        xaxis=dict(tickmode='linear', dtick=1)  # Ensure only 2018, 2019, 2020 appear
    )

    return fig

@app.callback(
    Output("nav-links", "children"),
    Input("nav-url", "pathname")
)
def update_active_link(pathname):
    return [
        dbc.NavLink("Dashboard", href="/", className=f"text-white {'fw-bold border-bottom border-2 border-white' if pathname == '/' else ''}"),
        dbc.NavLink("Prediction", href="/prediction", className=f"text-white {'fw-bold border-bottom border-2 border-white' if pathname == '/prediction' else ''}")
    ]



if __name__ == "__main__":
    # Render sets the PORT environment variable for you.
    port = int(os.environ.get("PORT", 8050))  # Default to 8050 if PORT is not set
    app.run(host="0.0.0.0", port=port)
