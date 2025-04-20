import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")
import joblib
model = joblib.load("code/wpp_model.pkl")

# Load and preprocess data
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

canal_options = [{'label': canal, 'value': canal} for canal in df['Canal_name (EN)'].unique() if canal != '#VALUE!']
year_options = [{'label': str(year), 'value': year} for year in sorted(df['year'].unique())]

# Sanitized feature IDs (for use in Dash components)
feature_info = {
    "ph": ("  pH", "pH"),
    "do": ("DO (mg/l)", "Dissolved Oxygen"),
    "tds": ("SS (mg/l)", "Suspended Solids"),
    "nh3n": ("NH3N (mg/l)", "Ammonia"),
    "temp": ("TEMP. (oC)", "Temperature"),
    "h2s": ("H2S (mg/l)", "Hydrogen Sulfide"),
    "bod": ("BOD (mg/l)", "BOD"),
    "cod": ("COD (mg/l)", "COD"),
    "tkn": ("TKN (mg/l)", "TKN"),
    "no2": ("NO2 (mg/l)", "NO2"),
    "no3": ("NO3 (mg/l)", "NO3"),
    "tp": ("T-P (mg/l)", "Total Phosphorus"),
    "coliform": ("T.Coliform (col/100ml)", "Coliform")
}


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Bangkok Water Dashboard"

navbar = html.Div([
    dcc.Location(id='nav-url', refresh=False),
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("Bangkok Water Quality", href="/", className="fw-semibold fs-4 text-white"),
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
        html.H2("Bangkok Water Quality Dashboard", className="text-center mt-4 mb-3"),

        dcc.Tabs(id="tabs", value='tab-main-graph', children=[
            dcc.Tab(label='Main Graph', value='tab-main-graph'),
            dcc.Tab(label='By Canal', value='tab-canal'),
            dcc.Tab(label='Trends', value='tab-trends'),
            dcc.Tab(label='Map View', value='tab-map'),
        ], colors={
            "border": "white",
            "primary": "black",
            "background": "#f7f7f7"
        }),

        html.Div(id='tabs-content', className='mt-4')
    ], fluid=False)

def prediction_layout():
    input_fields = list(feature_info.items())
    cols = [input_fields[i::3] for i in range(3)]

    return dbc.Container([
        html.H2("Water Quality Prediction", className="text-center mt-4 mb-4"),
        html.Div([
            dbc.Row([
                *[
                    dbc.Col([
                        html.Div([
                            dbc.Label(label, html_for=key),
                            dbc.Input(type="number", id=key, placeholder=f"Enter {label}", step="any", min=0, required=True)
                        ], className="mb-3") for key, (_, label) in group
                    ], md=4) for group in cols
                ]
            ], className="d-flex flex-wrap justify-content-center")
        ]),
        html.Div(className="text-center mt-3", children=[
            dbc.Button("Predict", id="predict-button", color="primary", className="me-2"),
            dbc.Button("Reset", id="reset-button", color="secondary", className="ms-2")
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Alert(id='prediction-output', color='info', className='mt-3')
            ])
        ])
    ], fluid=False)


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

# Prediction logic
@app.callback(
    Output('prediction-output', 'children'),
    Input('predict-button', 'n_clicks'),
    [State(key, 'value') for key in feature_info.keys()]
)
def predict_quality(n_clicks, *inputs):
    if not n_clicks:
        return dash.no_update

    if any(val is None for val in inputs):
        return "⚠️ Please fill in all fields before predicting."

    try:
        values = [float(x) for x in inputs]
        wqi = sum(values) / len(values)
        if wqi >= 70:
            label = "✅ Safe"
        elif wqi >= 50:
            label = "⚠️ Potentially Unsafe"
        else:
            label = "❌ Unsafe"
        return f"Predicted Water Quality Index: {wqi:.2f} → {label}"
    except Exception as e:
        return f"Error in prediction: {e}"

# Reset button logic
@app.callback(
    [Output(key, 'value') for key in feature_info.keys()],
    Input('reset-button', 'n_clicks')
)
def reset_fields(n):
    if not n:
        return dash.no_update
    return [None] * len(feature_info)

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
                    options=[
                        {'label': 'DO (mg/l)', 'value': 'DO (mg/l)'},
                        {'label': 'pH', 'value': '  pH'},
                        {'label': 'TEMP. (oC)', 'value': 'TEMP. (oC)'},
                        {'label': 'NH3N (mg/l)', 'value': 'NH3N (mg/l)'}
                    ],
                    value='DO (mg/l)',
                    clearable=False
                )
            ], md=6),
        ], className="mb-4"),

        dcc.Graph(id='canal-bar-graph')
    ])

    elif tab == 'tab-main-graph':
        return html.Div([
            html.Label("Select Year:"),
            dcc.Dropdown(id='year-dropdown', options=year_options, value=year_options[0]['value'], clearable=False),
            html.Label("Select Canal:", style={'marginTop': '10px'}),
            dcc.Dropdown(id='canal-dropdown', options=canal_options, value=canal_options[0]['value'], clearable=False),
            dcc.Graph(id='gauge-graph')
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
        return html.P("Map visualization placeholder", className="text-center")

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
    df_trend = aggregated_df[aggregated_df['Canal_name (EN)'] == selected_canal].copy()
    df_trend['year'] = df_trend['year'].astype(int)

    # Melt the dataframe to long format
    df_long = df_trend.melt(
        id_vars='year',
        value_vars=['DO (mg/l)', '  pH', 'SS (mg/l)'],
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


app.run(debug=True)
