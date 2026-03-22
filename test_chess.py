import pprint
from chessdotcom.client import Client
Client.request_config.setdefault("headers", {})
Client.request_config["headers"]["User-Agent"] = "ChessStatsApp/3.3 (your_email@example.com)"

from chessdotcom import get_player_stats, get_player_profile, get_player_games_by_month
try:
    stats = get_player_stats("hikaru")
    print("STATS keys:", stats.json["stats"].keys())
    print("Blitz stats:", stats.json["stats"].get("chess_blitz"))
except Exception as e:
    print(e)
