import sys, os

import pandas as pd
import dash, dash_table
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Output, Input

try:
    fileDir = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(fileDir)
    sys.path.insert(0, parentDir)
except:
    pass

from config import DEBUG
from utils.wmata_static import get_circuit_ids
from stream_analysis.train_pos_consumer import TrainPosRRCF
from stream_analysis.train_gtfs_consumer import TrainGTFS

circuits = get_circuit_ids()
stream_length = 20
line_colors = {'BLUE': 'blue', 'GR': 'green', 'OR': 'orange', 'RD': 'red', 'SV': 'grey', 'YL': 'yellow'}
marker_type = {1: 'triangle-right', 2: 'triangle-left'}
train_pos_rrcf = TrainPosRRCF()
train_gtfs = TrainGTFS()

if DEBUG:
    train_pos_rrcf.process_msgs(100)
    train_gtfs.process_msgs(1)

columns = ['cars', 'direction', 'circuit', 'seconds_at_loc', 'anomaly_score']
tbl_cols = [{"name": i, "id": i} for i in columns]

styles = [{
    'if': {
        'column_id': 'anomaly_score',
        'filter_query': '{anomaly_score} > 50'
    },
    'color': 'red',
}]


app = dash.Dash(__name__)

app.layout = html.Div()

# Circuit Anomaly Table
app.layout = html.Div([
    html.Div(id='table-wrapper',
             style={'width': 'auto', 'overflow-y': 'scroll','max-width': '90vw', 'margin':'0 auto 50px'},
             children=[
                 dash_table.DataTable(id='circuit_anomaly_table',
                                      data=[{}],
                                      columns=tbl_cols,
                                      style_cell={'textAlign': 'center','min-width':'50px'},
                                      filter_action="native",
                                      sort_action="native",
                                      # sort_mode="multi",
                                      column_selectable="single",
                                      row_selectable="multi",
                                      # row_deletable=True,
                                      selected_columns=[],
                                      selected_rows=[],
                                      page_action="native",
                                      page_current=0,
                                      page_size=15,
                                      style_data_conditional=styles
                                      ),
                 dcc.Interval(
                     id='graph-update',
                     interval=60 * 100,
                     n_intervals=0
                 ),
             ]),

    # GTFS Table
    html.Div(id='table-wrapper2',
             style={'width': 'auto', 'overflow-y': 'scroll','max-width': '90vw', 'margin':'0 auto 50px'},
             children=[
                 dash_table.DataTable(id='gtfs-table',
                                      data=[{}],
                                      columns=[],
                                      style_cell={'textAlign': 'center','min-width':'50px'},
                                      filter_action="native",
                                      sort_action="native",
                                      # sort_mode="multi",
                                      column_selectable="single",
                                      # row_deletable=True,
                                      page_action="native",
                                      page_current=0,
                                      page_size=15,
                                      ),
                 dcc.Interval(
                     id='gtfs-update',
                     interval=60 * 1000,
                     n_intervals=0
                 ),
             ]),

    # count-vs-time
    html.Div(id='table-wrapper3',
             style={'width': 'auto', 'overflow-y': 'scroll', 'max-width': '90vw', 'margin': '0 auto 50px'},
             children=[
                 dcc.Graph(id='count-vs-time', animate=True),
                 dcc.Interval(
                     id='count-vs-time-update',
                     interval=60 * 100,
                     n_intervals=0
                 ),
             ]),

    # timedif-vs-time
    html.Div(id='table-wrapper4',
             style={'width': 'auto', 'overflow-y': 'scroll', 'max-width': '90vw', 'margin': '0 auto 50px'},
             children=[
                 dcc.Graph(id='timedif-vs-time', animate=True),
                 dcc.Interval(
                     id='timedif-vs-time-update',
                     interval=60 * 100,
                     n_intervals=0
                 ),
             ]),

    # timedif-dist
    html.Div(id='table-wrapper5',
             style={'width': 'auto', 'overflow-y': 'scroll', 'max-width': '90vw', 'margin': '0 auto 50px'},
             children=[
                 dcc.Graph(
                     id='timedif-dist',
                     animate=True),
                 dcc.Interval(
                     id='timedif-dist-update',
                     interval=60 * 100,
                     n_intervals=0
                 ),
             ])
    ])

@app.callback(Output('circuit_anomaly_table', 'data'),
              [Input('graph-update', 'n_intervals')])
def update_circuit_anomalies_table(n_interval):
    train_pos_rrcf.process_msgs(1)
    scores = train_pos_rrcf.get_flattened_last_scores()

    return scores

@app.callback([Output('gtfs-table', 'data'),
               Output('gtfs-table', 'columns')],
              [Input('gtfs-update', 'n_intervals')])
def update_gtfs_table(n_interval):
    train_gtfs.process_msgs(1)
    df = train_gtfs.get_past_data()[0]
    cols = [{'name': col, 'id': col} for col in df.columns]
    data = df.to_dict('rows')
    return data, cols


@app.callback(Output('count-vs-time', 'figure'),
              [Input('count-vs-time-update', 'n_intervals')])
def update_gtfs_table(n_interval):
    line = 'BLUE'
    direction = 1
    dfs = train_gtfs.get_past_data(20)
    data = pd.concat(dfs)

    data['vehicle.timestamp'] = pd.to_datetime(data['vehicle.timestamp'], unit='s')
    min_dt = min(data['vehicle.timestamp'])
    max_dt = max(data['vehicle.timestamp'])

    d = data[
        (data['vehicle.trip.routeId'].str.contains(line)) & (data['vehicle.trip.directionId'] == direction)].groupby(
        'vehicle.timestamp').count()
    x = d.index
    y = d.id

    max_count = max(y)+1

    fig_data = []
    fig_data.append(go.Scatter(
        x=x,
        y=y,
        name=line,
        mode='lines+markers',
        marker=dict(
            color=line_colors[line],
            symbol=marker_type[direction],
            size=15
        )
    ))

    fig_layout = go.Layout(
        title='Train Count over Time',
        xaxis=dict(
            range=[min_dt, max_dt],
            title='Date/Time (UTC)'
        ),
        yaxis=dict(
            range=[0, max_count],
            title='Number of Trains'
        )

    )

    return {'data': fig_data, 'layout': fig_layout}


@app.callback(Output('timedif-vs-time', 'figure'),
              [Input('timedif-vs-time-update', 'n_intervals')])
def update_gtfs_table(n_interval):
    line = 'BLUE'
    direction = 1
    dfs = train_gtfs.get_past_data(20)
    data = pd.concat(dfs)

    data['vehicle.timestamp'] = pd.to_datetime(data['vehicle.timestamp'], unit='s')
    min_dt = min(data['vehicle.timestamp'])
    max_dt = max(data['vehicle.timestamp'])


    d = data[(data['vehicle.trip.routeId'].str.contains(line)) &
             (data['vehicle.trip.directionId'] == direction) &
             (~data.delta.isnull())
    ]

    x = d['vehicle.timestamp']
    y = d.delta / 60

    max_diff = max(y) + 1
    min_diff = min(y) - 1

    fig_data = []
    fig_data.append(go.Scatter(
        x=x,
        y=y,
        name=line,
        mode='markers',
        marker=dict(
            color=line_colors[line],
            symbol=marker_type[direction],
            size=15
        )
    ))

    fig_layout = go.Layout(
        title='Time of Arrival Difference (Actual - Expected) over Time',
        xaxis=dict(
            range=[min_dt, max_dt],
            title='Date/Time (UTC)'
        ),
        yaxis=dict(
            range=[min_diff, max_diff],
            title='Time Difference (s)'
        )

    )

    return {'data': fig_data, 'layout': fig_layout}


@app.callback(Output('timedif-dist', 'figure'),
              [Input('timedif-dist-update', 'n_intervals')])
def update_gtfs_table(n_interval):
    line = 'BLUE'
    direction = 1
    dfs = train_gtfs.get_past_data(20)
    data = pd.concat(dfs)

    d = data[
        (data['vehicle.trip.routeId'].str.contains(line)) &
        (data['vehicle.trip.directionId'] == direction) &
        (~data.delta.isnull())
    ]
    x = d.delta

    max_val = max(x) + 1
    min_val = min(x) - 1

    fig_data = []
    fig_data.append(go.Histogram(
        x=x,
        marker_color=line_colors[line],
        # title_text='Time of Arrival Difference (Actual - Expected)',
        # xaxis_title_text='Time Difference (s)',
        # yaxis_title_text='Count'
    ))

    fig_layout = go.Layout(
        title='Time of Arrival Difference (Actual - Expected)',
        xaxis=dict(
            range=[min_val, max_val],
            title='Time Difference (s)'
        ),
        yaxis=dict(
            title='Count'
        )

    )

    return {'data': fig_data, 'layout': fig_layout}


if __name__ == '__main__':
    app.run_server(debug=True)