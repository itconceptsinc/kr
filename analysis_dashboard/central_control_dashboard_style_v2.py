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
    update_gtfs_hist_callback, update_gtfs_preds_callback, line_colors

if DASHBOARD_DEBUG:
    update_interval = 60 * 1000
else:
    update_interval = 60 * 1000

columns = ['cars', 'direction', 'circuit', 'seconds_at_loc', 'anomaly_score']
tbl_cols = [{"name": i, "id": i} for i in columns]

styles = [{
    'if': {
        'column_id': 'anomaly_score',
        'filter_query': '{anomaly_score} > 15'
    },
    'color': 'red',
}]


app = dash.Dash(__name__)

app.layout = html.Div()

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.Img(
                            className="logo", src=app.get_asset_url("it-concepts-inc-logo-color-large.png")
                        ),
                        html.H2("KESSELRUN Demo App"),
                        html.P(
                            """Select different train lines using the selection box below."""
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                               #Area for Additional information
                            ],
                         ),
                        html.Div(
                            className="",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for train lines 
                                        dcc.Dropdown(
                                            id="line-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in line_colors
                                            ],
                                            value='BLUE',
                                            placeholder="Select a line",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        dcc.Markdown(
                            children=[
                                "Data Source: [General Transit Feed Specification](https://developers.google.com/transit)"
                            ]
                        ),
                        dcc.Markdown(
                            children=[
                                "Data Source: [WMATA API](https://developer.wmata.com/)"
                            ]
                        ),
                        #Information Panel
                        html.Div([
                            html.H3('Train Predictions:'),
                            html.P(id='gtfs-preds', children=['init']),
                            dcc.Interval(
                                id='gtfs-preds-update',
                                interval=update_interval,
                                n_intervals=0
                            )
                        ],
                            style={'padding-top': '40px'}
                        )
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        html.H2("KESSELRUN Processed Data"),
                        dcc.Tabs([
                            dcc.Tab(label='Circuit Anomaly Table', children = [
                                html.Div(id='table-wrapper-preds',
                                         style={'width': 'auto', 'overflow-y': 'scroll', 'max-width': '90vw',
                                                'margin': '0 auto 50px'},
                                         children=[
                                             html.Div([
                                                 """RRCF Anomaly scores for each cirucit of the metro rail lines. Scores
                                                 exceeding the set threshold are highlighted in """,
                                                 html.Span('red', style={'color': 'red'})
                                             ]),
                                             dash_table.DataTable(id='circuit_anomaly_table',
                                                                  data=[{}],
                                                                  columns=tbl_cols,
                                                                  style_cell={'textAlign': 'center', 'min-width': '50px'},
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
                                                                  page_size=10,
                                                                  style_data_conditional=styles
                                                                  ),
                                             dcc.Interval(
                                                 id='graph-update',
                                                 interval=update_interval,
                                                 n_intervals=0
                                             ),
                                         ]),
                                ]),
                            dcc.Tab(label='GTFS Table', children=[
                                # GTFS Table
                                html.Div(id='table-wrapper2',
                                         style={'width': 'auto', 'overflow-y': 'scroll', 'max-width': '90vw',
                                                'margin': '0 auto 50px'},
                                         children=[
                                             html.P(
                                                 """Live table of GTFS data provided by the WMATA API"""
                                             ),
                                             dash_table.DataTable(id='gtfs-table',
                                                              data=[{}],
                                                              columns=[],
                                                              style_cell={'textAlign': 'center', 'min-width': '50px'},
                                                              filter_action="native",
                                                              sort_action="native",
                                                              # sort_mode="multi",
                                                              column_selectable="single",
                                                              # row_deletable=True,
                                                              page_action="native",
                                                              page_current=0,
                                                              page_size=10,
                                                              ),
                                         dcc.Interval(
                                             id='gtfs-update',
                                             interval=update_interval,
                                             n_intervals=0
                                         ),
                                     ]),
                                ]),
                            dcc.Tab(label='Count vs Time', children=[
                            # count-vs-time
                                html.Div(id='table-wrapper3',
                                         style={'width': 'auto', 'overflow-y': 'scroll', 'max-width': '90vw',
                                                'margin': '0 auto 50px'},
                                         children=[
                                             html.P(
                                                """Visualization of the number of trains running on a given line and
                                                direction over the past couple hours"""
                                             ),
                                             dcc.Graph(id='count-vs-time', animate=True),
                                             dcc.Interval(
                                                 id='count-vs-time-update',
                                                 interval=update_interval,
                                                 n_intervals=0
                                             ),
                                         ]),
                            ]),
                            dcc.Tab(label='Time Diff vs Time Update', children=[
                                # timedif-vs-time
                            html.Div(id='table-wrapper4',
                                     style={'width': 'auto', 'overflow-y': 'scroll', 'max-width': '90vw',
                                            'margin': '0 auto 50px'},
                                     children=[
                                         html.P(
                                                """Visualization of the number of trains running ahead/behind/on-time
                                                for a given line and direction"""
                                         ),
                                         dcc.Graph(id='timedif-vs-time', animate=True),
                                         dcc.Interval(
                                             id='timedif-vs-time-update',
                                             interval=update_interval,
                                             n_intervals=0
                                         ),
                                     ]),
                        ]),
                            dcc.Tab(label='Time Diff Dist', children=[
                                # timedif-dist
                                html.Div(id='table-wrapper5',
                                         style={'width': 'auto', 'overflow-y': 'scroll', 'max-width': '90vw',
                                                'margin': '0 auto 50px'},
                                         children=[
                                             html.P(
                                                """Visaulization displaying the counts of trains that are running
                                                ahead/behind/on-time"""
                                             ),
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
                        ])

                    ],
                ),
            ],
        )
    ]
)

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
              [Input('count-vs-time-update', 'n_intervals'),
 	       Input('line-dropdown','value')])
def update_gtfs_table(n_interval,linecolor):
    return update_gtfs_time_hist_callback(linecolor)


@app.callback(Output('timedif-vs-time', 'figure'),
              [Input('timedif-vs-time-update', 'n_intervals'),
               Input('line-dropdown','value')])
def update_gtfs_table(n_interval,linecolor):
    return update_gtfs_time_diff_callback(linecolor)


@app.callback(Output('timedif-dist', 'figure'),
              [Input('timedif-dist-update', 'n_intervals'),
               Input('line-dropdown','value')])
def update_gtfs_table(n_interval,linecolor):
    return update_gtfs_hist_callback(linecolor)


if __name__ == '__main__':
    if DASHBOARD_DEBUG:
        #app.run_server(debug=DASHBOARD_DEBUG)
        app.run_server(host='0.0.0.0')
    else:
        app.run_server(host='0.0.0.0')
