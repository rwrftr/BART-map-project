# bart_arrivals.py

import csv
import requests
from datetime import datetime, timezone
from google.transit import gtfs_realtime_pb2
import sys
from contextlib import redirect_stdout
from collections import defaultdict

# 1. Static GTFS stops lookup
def load_stops(stops_file='google_transit_20250113-20250808_v10/stops.txt'):
    """
    Reads stops.txt and returns a dict mapping stop_id → stop_name, stop_code, etc.
    """
    stops = {}
    with open(stops_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Each stop_id maps to a dict of info about the stop
            stops[row['stop_id']] = {
                'name': row['stop_name'],
                'code': row['stop_code'],
                'lat': float(row['stop_lat']),
                'lon': float(row['stop_lon']),
                'platform': row.get('platform_code', '')
            }
    return stops

# 2. Fetch GTFS-RT feed and parse Protobuf
def fetch_trip_updates(url: str) -> gtfs_realtime_pb2.FeedMessage:
    # Requests the GTFS-RT protobuf feed from BART and parses it
    resp = requests.get(url)
    resp.raise_for_status()                       # error if not HTTP 200
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)
    return feed

# 3. Print all upcoming arrivals (not used in interactive, but useful for debugging)
def print_upcoming_arrivals(stop_lookup, trip_feed):
    now_ts = datetime.now(timezone.utc).timestamp()
    for entity in trip_feed.entity:
        if not entity.HasField('trip_update'):
            continue
        trip_id = entity.trip_update.trip.trip_id
        for stu in entity.trip_update.stop_time_update:
            sid = stu.stop_id
            arrival = stu.arrival
            if not arrival or not arrival.time:
                continue
            wait_secs = arrival.time - now_ts
            wait_mins = max(int(wait_secs // 60), 0)
            stop_info = stop_lookup.get(sid, {})
            stop_name = stop_info.get('name', 'Unknown stop')
            print(f"• Train {trip_id} → {stop_name} (stop {sid}) in {wait_mins} min")

# 4. Print next arrival per train (writes summary to file)
def print_next_arrival_per_train(stop_lookup, trip_feed, output_file='output6.txt'):
    now_ts = datetime.now(timezone.utc).timestamp()
    lines = []
    lines.append("="*60)
    lines.append(f"BART Next Train Arrivals - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("="*60)
    for entity in trip_feed.entity:
        if not entity.HasField('trip_update'):
            continue
        trip_id = entity.trip_update.trip.trip_id
        for stu in entity.trip_update.stop_time_update:
            sid = stu.stop_id
            arrival = stu.arrival
            if not arrival or not arrival.time:
                continue
            wait_secs = arrival.time - now_ts
            if wait_secs >= 0:
                wait_mins = max(int(wait_secs // 60), 0)
                stop_info = stop_lookup.get(sid, {})
                stop_name = stop_info.get('name', 'Unknown stop')
                lines.append("-"*40)
                lines.append(f"Train ID: {trip_id}")
                lines.append(f"Next Stop: {stop_name} (stop {sid})")
                lines.append(f"Arrives in: {wait_mins} min")
                lines.append("-"*40)
                break  # Only print the next stop for this train
    lines.append("="*60)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Output written to {output_file}")

# 5. Get arrivals for a station or group (core of interactive search)
def get_station_arrivals(stop_lookup, trip_feed, station_query):
    """
    Return a list of (train_id, minutes, stop_id, stop_name) for soonest arrivals at a station or group of platforms.
    If station_query matches a full stop_id, only that stop is shown.
    If station_query matches a base code (e.g. 'M40'), all stops starting with 'M40' are included.
    """
    now_ts = datetime.now(timezone.utc).timestamp()
    arrivals = []
    # Find all stop_ids that match the query (either exact or as a prefix)
    matching_stop_ids = [sid for sid in stop_lookup if sid.lower() == station_query.lower() or sid.lower().startswith(station_query.lower())]
    if not matching_stop_ids:
        # Also allow searching by station name
        matching_stop_ids = [sid for sid, info in stop_lookup.items() if station_query.lower() in info.get('name', '').lower()]
    for entity in trip_feed.entity:
        if not entity.HasField('trip_update'):
            continue
        trip_id = entity.trip_update.trip.trip_id
        for stu in entity.trip_update.stop_time_update:
            sid = stu.stop_id
            if sid not in matching_stop_ids:
                continue
            stop_info = stop_lookup.get(sid, {})
            stop_name = stop_info.get('name', 'Unknown stop')
            arrival = stu.arrival
            if not arrival or not arrival.time:
                continue
            wait_secs = arrival.time - now_ts
            if wait_secs >= 0:
                wait_mins = max(int(wait_secs // 60), 0)
                arrivals.append((trip_id, wait_mins, sid, stop_name))
                break  # Only the next stop for this train
    arrivals.sort(key=lambda x: x[1])
    return arrivals

# 6. Interactive console for user queries
def interactive_console(stop_lookup, trip_feed,):
    # Only show stations with arrivals, grouped by base code
    available_stops = stops_with_arrivals(stop_lookup, trip_feed)
    base_codes = {}
    platforms = defaultdict(list)
    for sid in available_stops:
        base = sid.split('-')[0]
        platforms[base].append(sid)
        if base not in base_codes:
            base_codes[base] = stop_lookup[sid]['name']
    
    print(
    "\n commands: " \
    "\n   'list stops' to see all available stops with upcoming arrivals, " \
    "\n   'list trains' to see current trains and their next stop, " \
    "\n   station code (e.g. 'M40'), " \
    "\n   stop_id (e.g. 'M40-1'), " \
    "\n   'train <number>' to see a train's schedule "
    "\n   or 'exit' to quit")
    while True:
        query = input("\nEnter station code, train and number, or command: ").strip()
        dual_print(f"\nEnter station code, train and number, or command: {query}")
        if query.lower() in ('exit', 'quit'):
            dual_print("Goodbye!")
            break
        elif query.lower() == "list trains":
            list_trains_with_next_stop(stop_lookup, trip_feed)
        elif query.lower() == "list stops":
            list_stops_with_arrivals(base_codes, platforms) 
        elif query.lower().startswith("train "):
            train_id = query.split(" ", 1)[1].strip()
            stops = get_train_schedule(stop_lookup, trip_feed, train_id)
            if not stops:
                dual_print(f"No schedule found for train {train_id}.")
            else:
                dual_print(f"\nUpcoming stops for train {train_id}:")
                dual_print("-"*50)
                for stop_name, sid, wait_mins in stops:
                    dual_print(f"{stop_name} (stop {sid}) in {wait_mins} min")
                dual_print("-"*50)
        else:
            arrivals = get_station_arrivals(stop_lookup, trip_feed, query)
            if not arrivals:
                dual_print("No arrivals found for that station. Try again.")
            else:
                dual_print(f"\nSoonest arrivals at '{query}':")
                dual_print("-" * 50)
                for train_id, wait_mins, sid, stop_name in arrivals[:10]:  # Show up to 10 soonest
                    dual_print(f"Train {train_id} → {stop_name} (stop {sid}) in {wait_mins} min")
                dual_print("-" * 50)

# 7. Helper: which stops have arrivals in the feed?
def stops_with_arrivals(stop_lookup, trip_feed):
    """Return a set of stop_ids that have at least one upcoming arrival."""
    now_ts = datetime.now(timezone.utc).timestamp()
    stops = set()
    for entity in trip_feed.entity:
        if not entity.HasField('trip_update'):
            continue
        for stu in entity.trip_update.stop_time_update:
            sid = stu.stop_id
            arrival = stu.arrival
            if not arrival or not arrival.time:
                continue
            wait_secs = arrival.time - now_ts
            if wait_secs >= 0:
                stops.add(sid)
    return stops

# 8. Get full train schedule
def get_train_schedule(stop_lookup, trip_feed, train_id_query):
    """Return a list of (stop_name, stop_id, minutes) for all future stops for a given train_id."""
    now_ts = datetime.now(timezone.utc).timestamp()
    for entity in trip_feed.entity:
        if not entity.HasField('trip_update'):
            continue
        trip_id = entity.trip_update.trip.trip_id
        if train_id_query == trip_id:
            stops = []
            for stu in entity.trip_update.stop_time_update:
                sid = stu.stop_id
                stop_info = stop_lookup.get(sid, {})
                stop_name = stop_info.get('name', 'Unknown stop')
                arrival = stu.arrival
                if not arrival or not arrival.time:
                    continue
                wait_secs = arrival.time - now_ts
                if wait_secs >= 0:
                    wait_mins = max(int(wait_secs // 60), 0)
                    stops.append((stop_name, sid, wait_mins))
            return stops
    return None

# 9. Main entry point
def main():
    TRIP_UPDATE_URL = 'http://api.bart.gov/gtfsrt/tripupdate.aspx'
    stops = load_stops('google_transit_20250113-20250808_v10/stops.txt')
    feed = fetch_trip_updates(TRIP_UPDATE_URL)
    # Write summary to file
    print_next_arrival_per_train(stops, feed, output_file='output6.txt')
    # Interactive session in console, but also log to file
    with open('output6.txt', 'a', encoding='utf-8') as f:
        interactive_console(stops, feed, log_file=f)

def dual_print(*args, **kwargs):
    """Prints to the console and appends the same output to output6.txt."""
    print(*args, **kwargs)
    with open("output6.txt", "a", encoding="utf-8") as f:
        print(*args, **kwargs, file=f)
        f.flush()

def list_trains_with_next_stop(stop_lookup, trip_feed, log_file=None):
    now_ts = datetime.now(timezone.utc).timestamp()
    dual_print("\nCurrent trains and their next stop:")
    dual_print("-"*60)
    for entity in trip_feed.entity:
        if not entity.HasField('trip_update'):
            continue
        trip_id = entity.trip_update.trip.trip_id
        for stu in entity.trip_update.stop_time_update:
            sid = stu.stop_id
            arrival = stu.arrival
            if not arrival or not arrival.time:
                continue
            wait_secs = arrival.time - now_ts
            if wait_secs >= 0:
                wait_mins = max(int(wait_secs // 60), 0)
                stop_info = stop_lookup.get(sid, {})
                stop_name = stop_info.get('name', 'Unknown stop')
                dual_print(f"Train {trip_id} → {stop_name} (stop {sid}) in {wait_mins} min")
                break  # Only the next stop for this train
    dual_print("-"*60)

def list_stops_with_arrivals(base_codes, platforms):
    """List all stops with upcoming arrivals."""
    dual_print("\nAvailable BART Stations with upcoming arrivals (grouped):")
    for base, name in sorted(base_codes.items(), key=lambda x: x[1]):
        plat_list = ', '.join(platforms[base])
        dual_print(f"  {name} (code: {base}, platforms: {plat_list})")
    

if __name__ == '__main__':
    main()