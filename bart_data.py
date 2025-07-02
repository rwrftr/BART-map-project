import typing
from google.transit import gtfs_realtime_pb2

def load_stops(stops_file: str = "google_transit_20250113-20250808_v10/stops.txt") -> dict:
    """
    Load GTFS static stops.txt into a dictionary.
    Returns: {stop_id: {name, code, lat, lon, ...}}
    """
    pass

def fetch_feed(url: str = "http://api.bart.gov/gtfsrt/tripupdate.aspx") -> gtfs_realtime_pb2.FeedMessage:
    """
    Fetch and parse the GTFS-Realtime protobuf feed.
    Returns: FeedMessage object.
    """
    pass

def prepare_data(feed: gtfs_realtime_pb2.FeedMessage, stops: dict) -> typing.Tuple[dict, dict]:
    """
    Process the feed and stops to build:
      - next_by_train: {train_id: (next_stop_id, minutes)}
      - by_stop: {stop_id: [(train_id, minutes)]}
    Returns: (next_by_train, by_stop)
    """
    pass

def get_train_schedule(feed: gtfs_realtime_pb2.FeedMessage, stops: dict, train_id: str) -> list:
    """
    Get all future stops and arrival times for a given train_id.
    Returns: [(stop_name, stop_id, minutes), ...]
    """
    pass

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