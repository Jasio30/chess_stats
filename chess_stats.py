import os
import json
import time
import threading
import webbrowser
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# External dependency
from chessdotcom import get_player_games_by_month
from chessdotcom.client import Client
from chessdotcom.errors import ChessDotComError


# ===== CONFIGURATION =====
PORT = 8001
INTERVAL_SECONDS = 5  # Match HTML refresh interval
RETENTION_DAYS = 30   # Delete files older than this many days

# ===== DIRECTORIES =====
DOCS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "ChessStats")
os.makedirs(DOCS_DIR, exist_ok=True)

# File paths inside Documents
HTML_FILE = os.path.join(DOCS_DIR, "stats.html")
OUTPUT_FILE = os.path.join(DOCS_DIR, "summary_stats.json")


# Custom User-Agent for API
Client.request_config.setdefault("headers", {})
Client.request_config["headers"]["User-Agent"] = "ChessStatsApp/3.3 (your_email@example.com)" # Replace with your email address, to avoid accidentally ddos-ing the Chess.com API


# ===== HTML CONTENT =====
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Chess Stats</title>
  <style>
    body {
      margin: 0;
      padding: 20px;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      color: #ffffff;
      background-color: rgba(0, 0, 0, 0);
      font-size: 32px;
      line-height: 1.4;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
    }
    .stat { margin-bottom: 10px; }
    .wins { color: #4CAF50; }
    .draws { color: #FFC107; }
    .losses { color: #F44336; }
    .update-time { font-size: 20px; color: #aaa; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="stat wins" id="wins">Wins: ?</div>
  <div class="stat draws" id="draws">Draws: ?</div>
  <div class="stat losses" id="losses">Losses: ?</div>
  <div class="update-time" id="updated">Last updated: ?</div>
  <script>
    async function updateStats() {
      try {
        const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
        const data = await res.json();
        document.getElementById("wins").textContent = "Wins: " + data[0];
        document.getElementById("draws").textContent = "Draws: " + data[1];
        document.getElementById("losses").textContent = "Losses: " + data[2];
        document.getElementById("updated").textContent = "Last updated: " + new Date().toLocaleTimeString();
      } catch (e) {
        console.error("Failed to load stats:", e);
      }
    }
    updateStats();
    setInterval(updateStats, 5000);
  </script>
</body>
</html>
"""


# ===== CLEANUP FUNCTION =====
def cleanup_old_files(directory: str, retention_days: int):
    """Delete files in the given directory older than retention_days, protecting active files."""
    now = time.time()
    cutoff = now - (retention_days * 86400)  # seconds in a day
    protected = {HTML_FILE, OUTPUT_FILE}

    deleted = 0
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        try:
            if (
                os.path.isfile(filepath) 
                and filepath not in protected
                and os.path.getmtime(filepath) < cutoff
            ):
                os.remove(filepath)
                deleted += 1
        except Exception:
            pass

    if deleted:
        print(f"🧹 Cleaned up {deleted} old file(s) older than {retention_days} days in {directory}")


# ===== CORE FUNCTIONS =====
def get_month_stats(username: str, year: int, month: int, start_date: datetime):
    """Fetch games for a specific month and calculate stats, filtering by start_date."""
    wins = draws = losses = 0
    try:
        response = get_player_games_by_month(username, year, month)
        games = response.json["games"]

        for game in games:
            # Game end time
            end_time = datetime.fromtimestamp(game["end_time"])
            if end_time < start_date:
                continue

            white = game["white"]["username"].lower()
            black = game["black"]["username"].lower()

            if username.lower() == white:
                result = game["white"]["result"]
            elif username.lower() == black:
                result = game["black"]["result"]
            else:
                continue

            if result == "win":
                wins += 1
            elif result in ["checkmated", "timeout", "resigned", "abandoned", "lose"]:
                losses += 1
            elif result in [
                "agreed", "stalemate", "repetition", "timevsinsufficient",
                "insufficient", "50move", "draw"
            ]:
                draws += 1

    except ChessDotComError:
        pass  # skip API errors

    return [wins, draws, losses]


def export_loop(username: str, start_date: datetime):
    """Loop that periodically updates stats in the JSON file, caching historical months."""
    # Cache for closed months: (year, month) -> [wins, draws, losses]
    history_cache = {}

    # Initialize file immediately to avoid 404s
    try:
        with open(OUTPUT_FILE, "w") as f:
            json.dump([0, 0, 0], f)
    except Exception as e:
        print(f"Error creating initial JSON file: {e}")

    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating stats for {username}...")
            
            now = datetime.now()
            
            total_wins = total_draws = total_losses = 0
            
            # Iterate from start_date year/month up to current year/month
            y, m = start_date.year, start_date.month
            
            while (y < now.year) or (y == now.year and m <= now.month):
                period = (y, m)
                is_past_month = (y < now.year) or (y == now.year and m < now.month)
                
                if is_past_month and period in history_cache:
                    w, d, l = history_cache[period]
                else:
                    w, d, l = get_month_stats(username, y, m, start_date)
                    if is_past_month:
                        history_cache[period] = [w, d, l]
                
                total_wins += w
                total_draws += d
                total_losses += l
                
                # Move to next month
                m += 1
                if m > 12:
                    m, y = 1, y + 1

            stats = [total_wins, total_draws, total_losses]

            with open(OUTPUT_FILE, "w") as f:
                json.dump(stats, f)

            print(f"Saved {OUTPUT_FILE}: {stats}")
            
        except Exception as e:
            print(f"Error in export loop: {e}")
            
        time.sleep(INTERVAL_SECONDS)


# ===== CUSTOM HTTP HANDLER =====
class CustomHandler(SimpleHTTPRequestHandler):
    """Serves files directly from Documents/ChessStats."""

    def translate_path(self, path):
        parsed = urlparse(path)
        clean_path = parsed.path.lstrip("/")
        return os.path.join(DOCS_DIR, clean_path)


# ===== MAIN SERVER STARTUP =====
def run_server():
    # Create HTML file in Documents folder
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    httpd = HTTPServer(("localhost", PORT), CustomHandler)
    url = f"http://localhost:{PORT}/stats.html"
    print(f"Server running at {url}")
    webbrowser.open(url)
    httpd.serve_forever()


# ===== MAIN ENTRY =====
if __name__ == "__main__":
    # Cleanup first
    cleanup_old_files(DOCS_DIR, RETENTION_DAYS)

    username = input("Enter chess.com username: ").strip()

    # Read start date interactively
    while True:
        date_str = input("Enter start date (YYYY-MM-DD): ").strip()
        try:
            start_date = datetime.strptime(date_str, "%Y-%m-%d")
            break
        except ValueError:
            print("❌ Invalid format. Please use YYYY-MM-DD (e.g. 2024-05-01)")

    print(f"\n✅ Tracking {username} since {start_date.date()}, updating every {INTERVAL_SECONDS}s...")
    print(f"📁 Files are stored in: {DOCS_DIR}")
    print(f"🧹 Files older than {RETENTION_DAYS} days are automatically deleted.\n")

    # Run API updater in background
    threading.Thread(target=export_loop, args=(username, start_date), daemon=True).start()

    # Run local web server
    run_server()
