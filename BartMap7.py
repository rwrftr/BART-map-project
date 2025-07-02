#!/usr/bin/env python3
"""
bartMap7.py: Simplified BART GTFS-Realtime client with interactive console.
Dependencies:
    pip install requests protobuf gtfs-realtime-bindings
    pip install sv-ttk
"""

import csv
import requests
import tkinter
import sv_ttk
from tkinter import ttk
from datetime import datetime, timezone
from collections import defaultdict
from google.transit import gtfs_realtime_pb2

# Paths and URLs
STOPS_FILE = 'google_transit_20250113-20250808_v10/stops.txt'
FEED_URL   = 'http://api.bart.gov/gtfsrt/tripupdate.aspx'

def load_stops(path=STOPS_FILE):
    """
    Load GTFS static stops.txt into a dictionary
    returns stops dict {stop_id: stop_name}

    """
    stops = {}
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            stops[row['stop_id']] = row['stop_name']
    return stops

def fetch_feed(url=FEED_URL):
    """
    GET the GTFS-Realtime protobuf feed and parse it.
    Returns a FeedMessage object.

    """
    resp = requests.get(url)
    resp.raise_for_status()
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)
    return feed

def prepare_data(feed, stops):
    """
    From a FeedMessage and stops mapping, build:
      - next_by_train: {trip_id: (stop_id, minutes_until)}
      - by_stop: {stop_id: [(trip_id, minutes_until), ...]}
    
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

def get_train_schedule(feed, stops, train_id):
    """
    Return full upcoming schedule for a given train_id as list of
    (stop_id, stop_name, minutes_until).
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

def interactive_console(stops, feed):
    """
    Simple REPL: commands:
      - list trains
      - list stops
      - train <trip_id>
      - <station code or name>
      - exit
    """
    next_by_train, by_stop = prepare_data(feed, stops)

    while True:
        cmd = (input( "Commands: 'list trains', 'list stops', station code or name, 'train <id>', 'exit'\n> ").strip()).lower() # cmd = input normalized

        if cmd in ('exit', 'quit'):
            print('Goodbye!')
            break

        if cmd == 'list trains':
            print()
            for tid, (sid, mins) in sorted(next_by_train.items()):
                print(f"Train {tid} → {stops.get(sid,'?')} ({sid}) in {mins} min")

        if cmd == 'list stops':
            print()
            for sid in sorted(by_stop):
                print(f"{stops.get(sid,'?')} ({sid})")

        elif cmd.startswith('train '):
            tid = cmd.split(maxsplit=1)[1]
            sched = get_train_schedule(feed, stops, tid)
            if not sched:
                print(f"No schedule found for train {tid}.")
            else:
                for sid, name, mins in sched:
                    print(f"{name} ({sid}) in {mins} min")

        else:
            # Station query: by stop_id prefix or name substring
            q = cmd
            matches = {sid for sid in by_stop if sid.lower().startswith(q)}
            matches |= {sid for sid,name in stops.items() if q in name.lower()}

            if not matches:
                print(f"No matching stops for '{cmd}'")
            else:
                for sid in sorted(matches):
                    for tid, mins in sorted(by_stop[sid], key=lambda x: x[1])[:5]:
                        print(f"Train {tid} → {stops.get(sid,'?')} ({sid}) in {mins} min")

        print()

def main():
    stops = load_stops()
    feed = fetch_feed()
    interactive_console(stops, feed)

if __name__ == '__main__':
    main()
