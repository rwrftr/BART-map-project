# bart_gtfs_rt.py
import requests
import time
from google.transit import gtfs_realtime_pb2

# BART GTFS-Realtime endpoints
TRIP_UPDATE_URL = 'http://api.bart.gov/gtfsrt/tripupdate.aspx'
ALERTS_URL      = 'http://api.bart.gov/gtfsrt/alerts.aspx'

def fetch_feed(url: str) -> gtfs_realtime_pb2.FeedMessage:
    """
    Fetches a GTFS-RT feed from `url` and returns a parsed FeedMessage.
    Raises an HTTPError if the request fails.
    """
    resp = requests.get(url)
    resp.raise_for_status()  # error if not 200
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)
    return feed

def main():
    # Trip updates
    trip_feed = fetch_feed(TRIP_UPDATE_URL)
    print(f"🔄 TripUpdate entities: {len(trip_feed.entity)}")

    # Service alerts
    alert_feed = fetch_feed(ALERTS_URL)
    print(f"🚨 Alert entities: {len(alert_feed.entity)}")

    # Show one example entry
    if trip_feed.entity:
        print("\nExample trip update:")
        print(trip_feed.entity[0])

    # get the first time update
    

if __name__ == "__main__":
    main()
