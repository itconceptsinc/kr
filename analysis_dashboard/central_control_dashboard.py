import sys, os

import dash, dash_table
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Output, Input

try:
    fileDir = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(fileDir)
    sys.path.insert(0, parentDir)
except:
    pass

from config import DASHBOARD_DEBUG
from analysis_dashboard.analysis_callbacks import update_circuit_anomalies_table_callback,\
    update_gtfs_table_callback, update_gtfs_time_hist_callback, update_gtfs_time_diff_callback,\
    update_gtfs_hist_callback, update_gtfs_preds_callback

if DASHBOARD_DEBUG:
    update_interval = 60 * 1000
else:
    update_interval = 60 * 1000

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
                     interval=update_interval,
                     n_intervals=0
                 ),
             ]),

    # Preds Table
    html.Div(id='table-wrapper-pred',
             style={'width': 'auto', 'max-width': '90vw', 'margin': '0 auto 50px'},
             children=[
                 html.P(id='gtfs-preds',
                        children=['init']),
                 dcc.Interval(
                     id='gtfs-preds-update',
                     interval=update_interval,
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
                     interval=update_interval,
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
                     interval=update_interval,
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
                     interval=update_interval,
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
                     interval=update_interval,
                     n_intervals=0
                 ),
             ])
    ])


@app.callback(Output('circuit_anomaly_table', 'data'),
              [Input('graph-update', 'n_intervals')])
def update_circuit_anomalies_table(n_interval):
    return update_circuit_anomalies_table_callback()


@app.callback(Output('gtfs-preds', 'children'),
              [Input('gtfs-preds-update', 'n_intervals')])
def update_gtfs_preds(n_interval):
    return update_gtfs_preds_callback()


@app.callback([Output('gtfs-table', 'data'),
               Output('gtfs-table', 'columns')],
              [Input('gtfs-update', 'n_intervals')])
def update_gtfs_table(n_interval):
    return update_gtfs_table_callback()


@app.callback(Output('count-vs-time', 'figure'),
              [Input('count-vs-time-update', 'n_intervals')])
def update_gtfs_table(n_interval):
    return update_gtfs_time_hist_callback()


@app.callback(Output('timedif-vs-time', 'figure'),
              [Input('timedif-vs-time-update', 'n_intervals')])
def update_gtfs_table(n_interval):
    return update_gtfs_time_diff_callback()


@app.callback(Output('timedif-dist', 'figure'),
              [Input('timedif-dist-update', 'n_intervals')])
def update_gtfs_table(n_interval):
    return update_gtfs_hist_callback()


if __name__ == '__main__':
    if DASHBOARD_DEBUG:
        #app.run_server(debug=DASHBOARD_DEBUG)
        app.run_server(host='0.0.0.0')
    else:
        app.run_server(host='0.0.0.0')
