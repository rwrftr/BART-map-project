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

def getNextByTrain(feed: gtfs_realtime_pb2.FeedMessage, stops: dict) -> dict:
    """
    Get the next stop and minutes for each train_id.
    Returns: {train_id: (stop_id, minutes)}
    """

    now = datetime.now(timezone.utc).timestamp()
    next_by_train = {}

    for ent in feed.entity:
        if not ent.trip_update:
            continue
        tid = ent.trip_update.trip.trip_id
        
        # Find the first upcoming stop for each trip
        for stu in ent.trip_update.stop_time_update:
            if tid not in next_by_train and stu.arrival and stu.arrival.time >= now:
                mins = int((stu.arrival.time - now) // 60)
                sid = stu.stop_id
                next_by_train[tid] = (sid, mins)
                break
    return next_by_train

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
                    stop_name = stops.get(sid, {}).get('name', 'Unknown')
                    schedule.append((stop_name, sid, mins))
            return schedule
    return []

def get_stop_arrivals(feed: gtfs_realtime_pb2.FeedMessage, stops: dict, stop_name: str) -> list:
    """
    Get all trains arriving soon at a given stop (by stop_id or name).
    Returns: [(train_id, minutes, stop_id, stop_name), ...]
    """

    now = datetime.now(timezone.utc).timestamp()
    arrivals = []
    stops_in_station = []
    
    # Find all stop_ids that match the given stop_name
    for stop_id, stop_info in stops.items():
        if stop_info.get('name') == stop_name:
            stops_in_station.append(stop_id)

    for ent in feed.entity:
        if not ent.trip_update:
            continue
        for stu in ent.trip_update.stop_time_update:
            if stu.stop_id in stops_in_station and stu.arrival and stu.arrival.time >= now:
                mins = int((stu.arrival.time - now) // 60)
                tid = ent.trip_update.trip.trip_id
                arrivals.append((tid, mins, stu.stop_id, stop_name))

    return arrivals

def get_all_stops(feed: gtfs_realtime_pb2.FeedMessage, stops: dict) -> dict:
    """
    Get all stops that have predictions from the static GTFS data.
    Returns: {stop_id: {name, code, lat, lon, ...}}
    """
    all_stops = {}

    for ent in feed.entity:
        if not ent.trip_update:
            continue
        tid = ent.trip_update.trip.trip_id
        for stu in ent.trip_update.stop_time_update:
            if not stu.arrival or not stu.arrival.time:
                continue

            stop_id = stu.stop_id
            stop_name = stops.get(stop_id, {}).get('name', 'Unknown')
            parent_station = stops.get(stop_id, {}).get('parent_station', 'None')

            if stop_name not in all_stops:
                all_stops[stop_name] = {
                    'stop_id': stop_id,
                    'name': stop_name,
                    'code': stops.get(stop_id, {}).get('code', 'N/A'),
                    'parent_station': parent_station,
                }
        
    return all_stops

def refresh_data(stops_file: str, feed_url: str) -> typing.Tuple[dict, gtfs_realtime_pb2.FeedMessage, dict, dict, dict]:
    """
    Reload stops and fetch the latest feed.
    Returns: (stops, feed, nextByTrain, byStop, allStops)
    """
    stops = load_stops(stops_file)
    feed = fetch_feed(feed_url)

    next_by_train = getNextByTrain(feed, stops)
    allStops = get_all_stops(feed, stops)

    return stops, feed, next_by_train, allStops

if __name__ == "__main__":

    #test the functions
    stops, feed, getNextByTrain, allStops = refresh_data(STOPS_FILE, FEED_URL)
    
    # test get all stops
    all_stops = get_all_stops(feed, stops)
    print("All Stops:", all_stops)

    # test get_stop_arrivals
    stop_name = 'Embarcadero'
    arrivals = get_stop_arrivals(feed, stops, stop_name)
    print(f"Arrivals at {stop_name}:", arrivals)