import typing
import csv
import requests
from datetime import datetime, timezone
from collections import defaultdict
from google.transit import gtfs_realtime_pb2

STOPS_FILE = 'google_transit_20250113-20250808_v10/stops.txt'
FEED_URL   = 'http://api.bart.gov/gtfsrt/tripupdate.aspx'

def load_stops(path: str = STOPS_FILE) -> dict:
    """
    Load GTFS static stops.txt into a dictionary.
    Returns: {stop_id: {name, code, lat, lon, ...}}
    """

    stops = {}
    
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            stops[row['stop_id']] = {'name': row['stop_name'],
                                     'code': row['stop_code'],
                                     'zone_id': row['zone_id'],
                                     'parent_station': row['parent_station'],
                                     'platform_code': row['platform_code'],}
        
    return stops

def fetch_feed(url: str = FEED_URL) -> gtfs_realtime_pb2.FeedMessage:
    """
    Fetch and parse the GTFS-Realtime protobuf feed.
    Returns: FeedMessage object.
    """

    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    return feed

def prepare_data(feed: gtfs_realtime_pb2.FeedMessage, stops: dict) -> typing.Tuple[dict, dict]:
    """
    Process the feed and stops to build:
      - next_by_train: {train_id: {(next_stop_id, minutes)}
      - by_stop: {stop_id: [(train_id, minutes)]}
    Returns: (next_by_train, by_stop)
    """

    now = datetime.now(timezone.utc).timestamp()
    next_by_train = {}
    by_stop = defaultdict(list)

    for ent in feed.entity:
        if not ent.trip_update:
            continue
        tid = ent.trip_update.trip.trip_id
        # Find the first upcoming stop for each trip
        for stu in ent.trip_update.stop_time_update:
            if stu.arrival and stu.arrival.time >= now:
                mins = int((stu.arrival.time - now) // 60)
                sid = stu.stop_id
                # Record only the next stop for this train
                if tid not in next_by_train:
                    next_by_train[tid] = (sid, mins)
                # Record arrival at this stop
                by_stop[sid].append((tid, mins))
                break
    return next_by_train, by_stop

def get_train_schedule(feed: gtfs_realtime_pb2.FeedMessage, stops: dict, train_id: str) -> list:
    """
    Get all future stops and arrival times for a given train_id.
    Returns: [(stop_name, stop_id, minutes), ...]
    """

    now = datetime.now(timezone.utc).timestamp()
    for ent in feed.entity:
        if ent.trip_update and ent.trip_update.trip.trip_id == train_id:
            schedule = []
            for stu in ent.trip_update.stop_time_update:
                if stu.arrival and stu.arrival.time >= now:
                    mins = int((stu.arrival.time - now) // 60)
                    sid = stu.stop_id
                    schedule.append((sid, stops.get(sid, 'Unknown'), mins))
            return schedule
    return []

def get_stop_arrivals(feed: gtfs_realtime_pb2.FeedMessage, stops: dict, stop_query: str) -> list:
    """
    Get all trains arriving soon at a given stop (by stop_id or name).
    Returns: [(train_id, minutes, stop_id, stop_name), ...]
    """
    pass

def refresh_data(stops_file: str, feed_url: str) -> typing.Tuple[dict, gtfs_realtime_pb2.FeedMessage]:
    """
    Reload stops and fetch the latest feed.
    Returns: (stops, feed)
    """
    pass