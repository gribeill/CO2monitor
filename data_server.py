import sqlite3
import numpy as np
import time
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H2(children="CO2 Sensor Data"),
    html.Div(id="current-value"),
    dcc.Graph(id='CO2-graph'),
    dcc.Graph(id='T-graph'),
    dcc.Graph(id='RH-graph'),
    html.Br(),
    html.Div([
        html.Label("Time Range"),
        dcc.Dropdown(id='time-range',
                 options=[{'label': 'Last Hour', 'value': '1H'},
                          {'label': 'Last 6 Hours', 'value': '6H'},
                          {'label': 'Last 12 Hours', 'value': '12H'},
                          {'label': 'All', 'value': 'ALL'}],
                 value='12H')]),
    dcc.Interval(id='interval-component',
                 interval=10*1000,
                 n_intervals=0)])

@app.callback(
        Output('current-value', 'children'),
        Output('CO2-graph', 'figure'),
        Output('T-graph', 'figure'),
        Output('RH-graph', 'figure'),
        Input('interval-component', 'n_intervals'),
        Input('time-range', 'value'))
def update_data(n, time_range):
    
    db = sqlite3.connect('/home/pi/CO2monitor/sensor_data.db') 

    if time_range == "ALL":
        query = 'SELECT * FROM data'
        df = pd.read_sql(query, con=db, parse_dates={'dt': {'unit': 's'}})
    else:
        hours = int(time_range[:-1])
        secs  = int(time.time()) - hours*3600
        query = 'SELECT * FROM data WHERE dt > :timeval'
        df = pd.read_sql(query, con=db, parse_dates={'dt': {'unit': 's'}},
                params={'timeval': secs})
    db.close()
    
    df['dt'] = df['dt'].dt.tz_localize('UTC').dt.tz_convert("US/Eastern")

    fig = px.line(df, x="dt", y="co2", markers=True)
    fig.update_layout(title="CO2 Readings", xaxis_title="Time", 
            yaxis_title="CO2 [ppm]")
    
    
    fig_t = px.line(df, x="dt", y="t", markers=True)
    fig_t.update_layout(title='Temperature', xaxis_title='Time',
            yaxis_title='T [F]')
    
    fig_rh = px.line(df, x="dt", y="rh", markers=True)
    fig_rh.update_layout(title='Relative Humidity', xaxis_title='Time',
            yaxis_title='RH')
    
    return f"Last reading: {df['co2'].iloc[-1]} ppm", fig, fig_t, fig_rh

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0")

