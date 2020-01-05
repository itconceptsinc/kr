import sys, os

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

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
line_colors = {'BL': 'blue', 'GR': 'green', 'OR': 'orange', 'RD': 'red', 'SV': 'grey', 'YL': 'yellow'}
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

app.layout = html.Div([
    html.Div(id='table-wrapper',
             style={'width': 'auto', 'overflow-y': 'scroll','max-width': '90vw', 'margin':'0 auto 50px'},
             children=[
                 # Circuit Anomaly Table
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

    html.Div(id='table-wrapper2',
             style={'width': 'auto', 'overflow-y': 'scroll','max-width': '90vw', 'margin':'0 auto 50px'},
             children=[
                 # GTFS Table
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
             ])
    ])

# app.layout = html.Div(
#     [
#         dash_table.DataTable(id='live-table',
#                       data=[],
#                       columns=columns,
#                       style_cell={'textAlign': 'center', 'min-width': '50px'},
#                       )
#         dcc.Interval(
#             id='graph-update',
#             interval=60*1000,
#             n_intervals=0
#         ),
#     ]
# )

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


if __name__ == '__main__':
    app.run_server(debug=True)