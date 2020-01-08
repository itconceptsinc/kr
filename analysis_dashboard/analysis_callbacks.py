import sys, os
import pandas as pd
import plotly.graph_objects as go

from datetime import datetime, timedelta

try:
    fileDir = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(fileDir)
    sys.path.insert(0, parentDir)
except:
    pass

from config import DASHBOARD_DEBUG
from utils.wmata_static import get_circuit_ids
from stream_analysis.train_pos_consumer import TrainPosRRCF
from stream_analysis.train_gtfs_consumer import TrainGTFS


circuits = get_circuit_ids()
stream_length = 20
line_colors = {'BLUE': 'blue', 'GREEN': 'green', 'ORANGE': 'orange', 'RED': 'red', 'SILVER': 'grey', 'YELLOW': 'yellow'}
marker_type = {1: 'triangle-right', 2: 'triangle-left'}
train_pos_rrcf = TrainPosRRCF()
train_gtfs = TrainGTFS()

if DASHBOARD_DEBUG:
    train_pos_rrcf.seek_to_n_last(80)
    train_gtfs.seek_to_n_last(80)
    train_pos_rrcf.process_msgs(80)
    train_gtfs.process_msgs(5)

else:
    train_pos_rrcf.seek_to_n_last(250)
    train_gtfs.seek_to_n_last(20)
    train_pos_rrcf.process_msgs(250)
    train_gtfs.process_msgs(20)

columns = ['cars', 'direction', 'circuit', 'seconds_at_loc', 'anomaly_score']
tbl_cols = [{"name": i, "id": i} for i in columns]

if os.path.exists('../static/stop_times.txt'):
    static_dir = '../static/'
else:
    static_dir = 'static/'

stop_times = pd.read_csv(f'{static_dir}stop_times.txt')
trips = pd.read_csv(f'{static_dir}trips.txt')
trips['service_id'] = trips.service_id.astype('int')
stops = pd.read_csv(f'{static_dir}stops.txt')
cals = pd.read_csv(f'{static_dir}calendar_dates.txt')


def update_circuit_anomalies_table_callback():
    train_pos_rrcf.process_msgs(1)
    scores = train_pos_rrcf.get_flattened_last_scores()

    return scores


def update_gtfs_preds_callback():
    """
    #This should be changed to whatever time we think is reasonable to restrict
    the data pull to (ie how far in time from now do we consider the realtime
    data to no longer describe the current state).  I'd suggest 3 hours at max
    """
    timemargin = 24  # in hours

    # User input -- dropdowns would be helpful and I can get you the names in the morning
    line = 'SILVER'
    stop = 'METRO CENTER METRO STATION'
    headsign = 'WIEHLE RESTON EAST'

    data = train_gtfs.get_past_data()[0]
    current_dt = datetime.fromtimestamp(int(data['vehicle.timestamp'].max()))

    stopid = stops[stops['stop_name'] == stop].stop_id.values[0]

    # get service_id(s) of interest
    sids = cals[pd.to_datetime(cals.date, format='%Y%m%d') == current_dt.date()].service_id

    posstrip = pd.DataFrame()
    for sid in sids:
        t = trips[(trips.route_id == line) & (trips.service_id == sid) & (trips.trip_headsign == headsign)]
        posstrip = pd.concat([posstrip, t])

    # get tripids from posstrip
    tripids = posstrip.trip_id.values

    poss_st = stop_times[(stop_times.stop_id == stopid) & (stop_times.trip_id.astype('str').isin(tripids))]

    # filter on hour >= current_dt.hour, min >= current_dt.min
    if current_dt.hour < 3:
        hourcomp = current_dt.hour + 24 + current_dt.minute / 60.
    else:
        hourcomp = current_dt.hour + current_dt.minute / 60.

    time_arr = poss_st.arrival_time.astype('str').str[0:2].astype('float') + (
                poss_st.arrival_time.astype('str').str[3:5].astype('float') / 60.)

    poss_st2 = poss_st[time_arr > hourcomp]

    # first expected arrival time

    delta_time_data = data[(data['vehicle.trip.routeId'] == line) & (
                pd.to_datetime(data['vehicle.timestamp'], unit='s') >= current_dt - timedelta(
            hours=timemargin)) & (data['vehicle.trip.directionId'].astype('float') == posstrip.direction_id.values[
        0]) & (~data.delta.isnull()) & (~(data.delta > 10000))]

    delta_time_max = delta_time_data.delta.quantile(0.95)
    delta_time_min = delta_time_data.delta.quantile(0.05)

    if int(poss_st2.iloc[0].arrival_time[0:2]) <= 3:
        tmpval = str(int(poss_st2.iloc[0].arrival_time[0:2]) - 24) + poss_st2.iloc[0].arrival_time[2:]
        Arrival_Prediction_max = (
                    pd.to_datetime(tmpval, format='%H:%M:%S') + timedelta(seconds=delta_time_max)).strftime(
            '%H:%M')
        Arrival_Prediction_min = (
                    pd.to_datetime(tmpval, format='%H:%M:%S') + timedelta(seconds=delta_time_min)).strftime(
            '%H:%M')
    else:
        Arrival_Prediction_max = (pd.to_datetime(poss_st2.iloc[0].arrival_time, format='%H:%M:%S') + timedelta(
            seconds=delta_time_max)).strftime('%H:%M')
        Arrival_Prediction_min = (pd.to_datetime(poss_st2.iloc[0].arrival_time, format='%H:%M:%S') + timedelta(
            seconds=delta_time_min)).strftime('%H:%M')

    return f'Next arrival at {stop} going to {headsign} predicted between {Arrival_Prediction_min}-{Arrival_Prediction_max}'

def update_gtfs_table_callback():
    train_gtfs.process_msgs(1)
    df = train_gtfs.get_past_data()[0]
    cols = [{'name': col, 'id': col} for col in df.columns]
    data = df.to_dict('rows')
    return data, cols


def update_gtfs_time_hist_callback(linecolor):
    line = linecolor #'BLUE'
    direction = 1
    dfs = train_gtfs.get_past_data(stream_length)
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


def update_gtfs_time_diff_callback(linecolor):
    line = linecolor #'BLUE'
    direction = 1
    dfs = train_gtfs.get_past_data(stream_length)
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

    if len(y) > 0:
        max_diff = max(y) + 1
        min_diff = min(y) - 1
    else:
        max_diff = min_diff = 0

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


def update_gtfs_hist_callback(linecolor):
    line = linecolor.upper() #'BLUE'
    direction = 1
    dfs = train_gtfs.get_past_data(stream_length)
    data = pd.concat(dfs)

    d = data[
        (data['vehicle.trip.routeId'].str.contains(line)) &
        (data['vehicle.trip.directionId'] == direction) &
        (~data.delta.isnull())
    ]
    x = d.delta

    if len(x) > 0:
        max_val = max(x) + 1
        min_val = min(x) - 1
    else:
        min_val = max_val = 0

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
