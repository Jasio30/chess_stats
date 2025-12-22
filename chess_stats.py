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
# This is the default dashboard template. 
# To customize, you can edit the 'stats.html' file directly in your Documents/ChessStats folder.
# The script will only recreate this file if it is deleted.
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chess.com Live Stats</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-color: rgba(15, 15, 15, 0.85);
      --accent-win: #00fa9a;
      --accent-draw: #ffce54;
      --accent-loss: #ff4d4d;
      --text-main: #ffffff;
      --text-sub: #b0b0b0;
      --glass-border: rgba(255, 255, 255, 0.1);
    }

    body {
      margin: 0;
      padding: 0;
      font-family: 'Outfit', sans-serif;
      display: flex;
      justify-content: flex-start;
      align-items: flex-start;
      height: 100vh;
      background-color: transparent; /* Perfect for OBS overlays */
      overflow: hidden;
    }

    .dashboard {
      background: var(--bg-color);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--glass-border);
      border-radius: 16px;
      padding: 24px;
      margin: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
      min-width: 280px;
      animation: slideIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes slideIn {
      from { transform: translateX(-30px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    .header {
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid var(--glass-border);
      padding-bottom: 12px;
      margin-bottom: 4px;
    }

    .header h1 {
      font-size: 18px;
      font-weight: 800;
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--text-main);
    }

    .stats-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .stat-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 24px;
      font-weight: 600;
      transition: transform 0.2s ease;
    }

    .label {
      font-size: 14px;
      font-weight: 400;
      color: var(--text-sub);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .value {
      font-variant-numeric: tabular-nums;
    }

    .win { color: var(--accent-win); text-shadow: 0 0 15px rgba(0, 250, 154, 0.3); }
    .draw { color: var(--accent-draw); text-shadow: 0 0 15px rgba(255, 206, 84, 0.3); }
    .loss { color: var(--accent-loss); text-shadow: 0 0 15px rgba(255, 77, 77, 0.3); }

    .ratio-bar {
      height: 6px;
      width: 100%;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
      overflow: hidden;
      display: flex;
      margin-top: 8px;
    }

    .bar-segment {
      height: 100%;
      transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .bar-win { background: var(--accent-win); }
    .bar-draw { background: var(--accent-draw); }
    .bar-loss { background: var(--accent-loss); }

    .footer {
      font-size: 11px;
      color: var(--text-sub);
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
    }

    .dot {
      width: 6px;
      height: 6px;
      background: var(--accent-win);
      border-radius: 50%;
      display: inline-block;
      margin-right: 6px;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 250, 154, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(0, 250, 154, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 250, 154, 0); }
    }
  </style>
</head>
<body>
  <div class="dashboard">
    <div class="header">
      <h1>Session Stats</h1>
    </div>
    <div class="stats-container">
      <div class="stat-row">
        <span class="label">Wins</span>
        <span class="value win" id="wins">0</span>
      </div>
      <div class="stat-row">
        <span class="label">Draws</span>
        <span class="value draw" id="draws">0</span>
      </div>
      <div class="stat-row">
        <span class="label">Losses</span>
        <span class="value loss" id="losses">0</span>
      </div>
      
      <div class="ratio-bar">
        <div id="bar-win" class="bar-segment bar-win" style="width: 0%"></div>
        <div id="bar-draw" class="bar-segment bar-draw" style="width: 0%"></div>
        <div id="bar-loss" class="bar-segment bar-loss" style="width: 0%"></div>
      </div>
    </div>
    
    <div class="footer">
      <span><span class="dot"></span>LIVE UPDATING</span>
      <span id="updated">--:--:--</span>
    </div>
  </div>

  <script>
    let currentStats = [0, 0, 0];

    function animateValue(id, start, end, duration) {
      if (start === end) return;
      const range = end - start;
      let current = start;
      const increment = end > start ? 1 : -1;
      const stepTime = Math.abs(Math.floor(duration / range));
      const obj = document.getElementById(id);
      
      const timer = setInterval(function() {
        current += increment;
        obj.textContent = current;
        if (current == end) {
          clearInterval(timer);
        }
      }, stepTime || 10);
    }

    async function updateStats() {
      try {
        const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
        const data = await res.json();
        
        const w = data[0];
        const d = data[1];
        const l = data[2];
        const total = w + d + l || 1;

        // Animate numbers
        animateValue("wins", currentStats[0], w, 500);
        animateValue("draws", currentStats[1], d, 500);
        animateValue("losses", currentStats[2], l, 500);
        
        currentStats = [w, d, l];

        // Update bars
        document.getElementById("bar-win").style.width = ((w / total) * 100) + "%";
        document.getElementById("bar-draw").style.width = ((d / total) * 100) + "%";
        document.getElementById("bar-loss").style.width = ((l / total) * 100) + "%";

        document.getElementById("updated").textContent = new Date().toLocaleTimeString();
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
    # Create HTML file in Documents folder ONLY if it doesn't exist
    if not os.path.exists(HTML_FILE):
        print(f"📄 Creating default dashboard at {HTML_FILE}")
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_CONTENT)
    else:
        print(f"📄 Using existing dashboard at {HTML_FILE}")

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
