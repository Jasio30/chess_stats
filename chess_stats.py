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
INTERVAL_SECONDS = 15  # Update from chess.com every 15s to avoid rate limits
HTML_REFRESH_INTERVAL = 5 # Refresh dashboard from local JSON every 5s
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
  <title>Chess Stats Live Tracker</title>
  <script>
      let currentPresetVersion = null;
      setInterval(async () => {
          try {
              let res = await fetch("/version.json?_=" + new Date().getTime());
              let data = await res.json();
              if (currentPresetVersion === null) {
                  currentPresetVersion = data.version;
              } else if (currentPresetVersion !== data.version) {
                  location.reload();
              }
          } catch(e) {}
      }, 2000);
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
  <style>
    /* Automatically scale up the entire overlay for higher native resolution in OBS */
    body {
      zoom: 2.5; 
      transform-origin: top left;
    }
    :root {
      --bg-color: rgba(15, 15, 20, 0.75);
      --accent-win: #00fa9a;
      --accent-draw: #a0a0a0;
      --accent-loss: #ff4d4d;
      --accent-rating: #4da6ff;
      --text-main: #ffffff;
      --text-sub: #b0b0b0;
      --glass-border: rgba(255, 255, 255, 0.15);
      --glass-glow: rgba(255, 255, 255, 0.05);
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
      color: var(--text-main);
    }

    .dashboard {
      background: var(--bg-color);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--glass-border);
      border-radius: 20px;
      padding: 24px 28px;
      margin: 20px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), inset 0 0 20px var(--glass-glow);
      min-width: 320px;
      animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes fadeIn {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--glass-border);
      padding-bottom: 16px;
    }

    .header-title h1 {
      font-size: 20px;
      font-weight: 800;
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      background: linear-gradient(90deg, #fff, #aaa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .header-rating {
      text-align: right;
    }
    
    .rating-label {
      font-size: 11px;
      text-transform: uppercase;
      color: var(--text-sub);
      letter-spacing: 1px;
      margin-bottom: 2px;
    }
    
    .rating-value {
      font-size: 24px;
      font-weight: 800;
      color: var(--accent-rating);
      text-shadow: 0 0 15px rgba(77, 166, 255, 0.4);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .rating-change {
      font-size: 14px;
      font-weight: 600;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(255,255,255,0.1);
    }
    .change-pos { color: var(--accent-win); background: rgba(0,250,154,0.15); }
    .change-neg { color: var(--accent-loss); background: rgba(255,77,77,0.15); }
    .change-neu { color: var(--text-sub); }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }

    .stat-card {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--glass-border);
      border-radius: 12px;
      padding: 16px 12px;
      text-align: center;
      transition: transform 0.3s ease;
    }

    .stat-card:hover { transform: translateY(-3px); }

    .stat-label {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-sub);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    .stat-val {
      font-size: 32px;
      font-weight: 800;
      font-variant-numeric: tabular-nums;
    }

    .win { color: var(--accent-win); text-shadow: 0 0 15px rgba(0, 250, 154, 0.4); }
    .draw { color: var(--accent-draw); text-shadow: 0 0 15px rgba(160, 160, 160, 0.4); }
    .loss { color: var(--accent-loss); text-shadow: 0 0 15px rgba(255, 77, 77, 0.4); }

    .ratio-bar {
      height: 8px;
      width: 100%;
      background: rgba(0, 0, 0, 0.5);
      border-radius: 4px;
      overflow: hidden;
      display: flex;
      box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);
    }

    .bar-segment {
      height: 100%;
      transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .bar-win { background: linear-gradient(90deg, #00c679, var(--accent-win)); box-shadow: 0 0 10px rgba(0, 250, 154, 0.5); }
    .bar-draw { background: linear-gradient(90deg, #7a7a7a, var(--accent-draw)); }
    .bar-loss { background: linear-gradient(90deg, #e60000, var(--accent-loss)); box-shadow: 0 0 10px rgba(255, 77, 77, 0.5); }

    .footer {
      font-size: 11px;
      color: var(--text-sub);
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 4px;
    }

    .live-indicator {
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 600;
      letter-spacing: 0.5px;
    }

    .dot {
      width: 8px;
      height: 8px;
      background: var(--accent-win);
      border-radius: 50%;
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
      <div class="header-title">
        <h1>Session</h1>
      </div>
      <div class="header-rating">
        <div class="rating-label">Live Rating</div>
        <div class="rating-value">
          <span id="rating">----</span>
          <span id="rating-change" class="rating-change change-neu">+0</span>
        </div>
      </div>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Wins</div>
        <div class="stat-val win" id="wins">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Draws</div>
        <div class="stat-val draw" id="draws">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Losses</div>
        <div class="stat-val loss" id="losses">0</div>
      </div>
    </div>
    
    <div class="ratio-bar">
      <div id="bar-win" class="bar-segment bar-win" style="width: 0%"></div>
      <div id="bar-draw" class="bar-segment bar-draw" style="width: 0%"></div>
      <div id="bar-loss" class="bar-segment bar-loss" style="width: 0%"></div>
    </div>
    
    <div class="footer">
      <div class="live-indicator"><div class="dot"></div>LIVE</div>
      <div id="updated">--:--:--</div>
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
        
        const w = data[0] || 0;
        const d = data[1] || 0;
        const l = data[2] || 0;
        const rating = data[3] || 0;
        const rChange = data[4] || 0;
        
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

        // Update rating
        document.getElementById("rating").textContent = rating > 0 ? rating : "----";
        
        // Update rating change
        const rChangeEl = document.getElementById("rating-change");
        rChangeEl.textContent = (rChange > 0 ? "+" : "") + rChange;
        rChangeEl.className = "rating-change " + (rChange > 0 ? "change-pos" : (rChange < 0 ? "change-neg" : "change-neu"));

        document.getElementById("updated").textContent = new Date().toLocaleTimeString();
      } catch (e) {
        console.error("Failed to load stats:", e);
      }
    }

    updateStats();
    setInterval(updateStats, REFRESH_RATE);
  </script>
</body>
</html>
""".replace("REFRESH_RATE", str(HTML_REFRESH_INTERVAL * 1000))


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
                and (filename.startswith("stats") or filename.startswith("summary_stats"))
                and os.path.getmtime(filepath) < cutoff
            ):
                os.remove(filepath)
                deleted += 1
        except Exception:
            pass

    if deleted:
        print(f"🧹 Cleaned up {deleted} old tracking file(s) older than {retention_days} days in {directory}")


# ===== CORE FUNCTIONS =====
def get_month_stats(username: str, year: int, month: int, start_date: datetime):
    """Fetch games for a specific month and calculate stats, filtering by start_date."""
    wins = draws = losses = 0
    current_rating = 0
    starting_rating = 0
    
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

            result = None
            player_rating = 0
            
            if username.lower() == white:
                result = game["white"]["result"]
                player_rating = game["white"].get("rating", 0)
            elif username.lower() == black:
                result = game["black"]["result"]
                player_rating = game["black"].get("rating", 0)
            else:
                continue
                
            # Track ratings
            if starting_rating == 0 and player_rating > 0:
                starting_rating = player_rating
            if player_rating > 0:
                current_rating = player_rating

            if result == "win":
                wins += 1
            elif result in ["checkmated", "timeout", "resigned", "abandoned", "lose"]:
                losses += 1
            elif result in [
                "agreed", "stalemate", "repetition", "timevsinsufficient",
                "insufficient", "50move", "draw", "repetition", "timevsinsufficient"
            ]:
                draws += 1

        return {
            "stats": [wins, draws, losses],
            "current_rating": current_rating,
            "starting_rating": starting_rating,
            "success": True
        }
    except ChessDotComError as e:
        print(f"API Error fetching {year}-{month:02d}: {e}")
        return {
            "stats": [0, 0, 0],
            "current_rating": 0,
            "starting_rating": 0,
            "success": False
        }
    except Exception as e:
        print(f"Error fetching API for {year}-{month:02d}: {e}")
        return {
            "stats": [0, 0, 0],
            "current_rating": 0,
            "starting_rating": 0,
            "success": False
        }


TRACKER_STATE = {"username": None, "start_date": None}
EXPORT_THREAD_STARTED = False

def export_loop():
    """Loop that periodically updates stats in the JSON file, caching historical months."""
    # Cache for closed months: (year, month) -> stats dict
    history_cache = {}
    current_username = None
    current_start_date = None

    # Initialize file immediately to avoid 404s
    try:
        with open(OUTPUT_FILE, "w") as f:
            json.dump([0, 0, 0, 0, 0], f)
    except Exception as e:
        print(f"Error creating initial JSON file: {e}")

    while True:
        try:
            target_usr = TRACKER_STATE["username"]
            target_date = TRACKER_STATE["start_date"]
            
            if not target_usr or not target_date:
                time.sleep(1)
                continue
                
            if target_usr != current_username or target_date != current_start_date:
                history_cache.clear()
                current_username = target_usr
                current_start_date = target_date
                print(f"\\n✅ Tracking {current_username} since {current_start_date.date()}...")
                
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating stats for {current_username}...")
            
            now = datetime.now()
            
            total_wins = total_draws = total_losses = 0
            global_start_rating = 0
            latest_rating = 0
            
            # Iterate from start_date year/month up to current year/month
            y, m = current_start_date.year, current_start_date.month
            
            while (y < now.year) or (y == now.year and m <= now.month):
                period = (y, m)
                is_past_month = (y < now.year) or (y == now.year and m < now.month)
                
                if is_past_month and period in history_cache:
                    data = history_cache[period]
                    w, d, l = data["stats"]
                    sr = data["starting_rating"]
                    cr = data["current_rating"]
                else:
                    res = get_month_stats(current_username, y, m, current_start_date)
                    if not res["success"]:
                        raise Exception(f"API fetch failed for {y}-{m:02d}, skipping cycle.")
                    
                    w, d, l = res["stats"]
                    sr = res["starting_rating"]
                    cr = res["current_rating"]
                    
                    if is_past_month:
                        history_cache[period] = {
                            "stats": [w, d, l],
                            "starting_rating": sr,
                            "current_rating": cr
                        }
                
                total_wins += w
                total_draws += d
                total_losses += l
                
                if global_start_rating == 0 and sr > 0:
                    global_start_rating = sr
                if cr > 0:
                    latest_rating = cr
                
                # Move to next month
                m += 1
                if m > 12:
                    m, y = 1, y + 1

            rating_change = 0
            if global_start_rating > 0 and latest_rating > 0:
                rating_change = latest_rating - global_start_rating

            stats = [total_wins, total_draws, total_losses, latest_rating, rating_change]

            with open(OUTPUT_FILE, "w") as f:
                json.dump(stats, f)

            print(f"Saved {OUTPUT_FILE}: W:{total_wins} D:{total_draws} L:{total_losses} | Rating: {latest_rating} ({rating_change:+d})")
            
        except Exception as e:
            print(f"Skipped update: {e}")
            
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
    # Always update the default dashboard so the latest UI changes flow through
    print(f"📄 Updating dashboard template at {HTML_FILE}")
    try:
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_CONTENT)
    except Exception as e:
        print(f"⚠️ Could not write {HTML_FILE}: {e}")

    # Set up HTTP server options to avoid "Address already in use" if restarting quickly
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer(("localhost", PORT), CustomHandler)
    url = f"http://localhost:{PORT}/stats.html"
    print(f"Server running at {url}")
    webbrowser.open(url)
    httpd.serve_forever()


# ===== MAIN ENTRY =====
import tkinter as tk
from tkinter import ttk, messagebox
import sys

PREFS_FILE = os.path.join(DOCS_DIR, "user_prefs.json")

class StatsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess.com Live Stats Setup")
        self.root.geometry("450x440")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icon.png")
        if os.path.exists(icon_path):
            try:
                from PIL import Image, ImageTk
                icon_img = ImageTk.PhotoImage(Image.open(icon_path))
                self.root.iconphoto(False, icon_img)
            except Exception as e:
                print(f"Warning: Could not load app icon: {e}")
                
        # Force Dark Mode Titlebar on Windows 10/11
        try:
            import ctypes
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int(2)))
        except:
            pass
        
        self.bg_color = "#0f0f14"
        self.fg_color = "#ffffff"
        self.accent_color = "#00fa9a"
        self.input_bg = "#1e1e24"
        
        self.root.configure(bg=self.bg_color)
        
        self.prefs = {"username": "", "start_date": datetime.now().strftime("%Y-%m-%d"), "preset": "Default (Built-in)"}
        if os.path.exists(PREFS_FILE):
            try:
                with open(PREFS_FILE, "r") as f:
                    self.prefs.update(json.load(f))
            except:
                pass
                
        script_dir = os.path.dirname(os.path.abspath(__file__))
        presets_dir = os.path.join(script_dir, "presetsHTML")
        self.presets = ["Default (Built-in)"]
        self.preset_files = {}
        if os.path.exists(presets_dir):
            for f in os.listdir(presets_dir):
                if f.endswith(".html"):
                    ui_name = f.replace(".html", "").replace("_", " ").title()
                    self.presets.append(ui_name)
                    self.preset_files[ui_name] = os.path.join(presets_dir, f)
                    
        saved_preset = self.prefs.get("preset", "")
        if saved_preset.endswith(".html"):
            saved_preset = saved_preset.replace(".html", "").replace("_", " ").title()
            self.prefs["preset"] = saved_preset
            
        if self.prefs.get("preset") not in self.presets:
            self.prefs["preset"] = "Default (Built-in)"

        self.var_username = tk.StringVar(value=self.prefs["username"])
        self.var_date = tk.StringVar(value=self.prefs["start_date"])
        self.var_preset = tk.StringVar(value=self.prefs["preset"])
        
        global HTML_CONTENT
        self.default_html = HTML_CONTENT
        
        self.setup_ui()
        
    def setup_ui(self):
        font_title = ("Segoe UI", 16, "bold")
        font_lbl = ("Segoe UI", 10)
        font_inp = ("Segoe UI", 11)
        
        header = tk.Label(self.root, text="SESSION SETUP", bg=self.bg_color, fg=self.accent_color, font=font_title, pady=15)
        header.pack(fill=tk.X)
        
        container = tk.Frame(self.root, bg=self.bg_color, padx=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text="CHESS.COM USERNAME", bg=self.bg_color, fg="#888888", font=font_lbl).pack(anchor=tk.W, pady=(0,2))
        self.ent_user = tk.Entry(container, textvariable=self.var_username, font=font_inp, bg=self.input_bg, fg=self.fg_color, relief=tk.FLAT, insertbackground=self.fg_color)
        self.ent_user.pack(fill=tk.X, pady=(0,15), ipady=5)

        tk.Label(container, text="START DATE (YYYY-MM-DD)", bg=self.bg_color, fg="#888888", font=font_lbl).pack(anchor=tk.W, pady=(0,2))
        self.ent_date = tk.Entry(container, textvariable=self.var_date, font=font_inp, bg=self.input_bg, fg=self.fg_color, relief=tk.FLAT, insertbackground=self.fg_color)
        self.ent_date.pack(fill=tk.X, pady=(0,15), ipady=5)

        tk.Label(container, text="DASHBOARD PRESET", bg=self.bg_color, fg="#888888", font=font_lbl).pack(anchor=tk.W, pady=(0,2))
        
        # Style the combobox field
        style = ttk.Style()
        try:
            style.theme_use('clam')
            style.configure("TCombobox", fieldbackground=self.input_bg, background=self.bg_color, foreground=self.fg_color, insertcolor=self.fg_color)
            style.map('TCombobox',
                fieldbackground=[('readonly', self.input_bg)],
                selectbackground=[('readonly', self.input_bg)],
                selectforeground=[('readonly', self.fg_color)],
                foreground=[('readonly', self.fg_color)],
                background=[('readonly', self.bg_color)]
            )
        except:
            pass
            
        # Style the drop-down listbox
        self.root.option_add('*TCombobox*Listbox.background', self.input_bg)
        self.root.option_add('*TCombobox*Listbox.foreground', self.fg_color)
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.accent_color)
        self.root.option_add('*TCombobox*Listbox.selectForeground', '#000000')
        self.root.option_add('*TCombobox*Listbox.font', font_inp)
            
        self.cb = ttk.Combobox(container, textvariable=self.var_preset, values=self.presets, state="readonly", font=font_inp)
        self.cb.pack(fill=tk.X, pady=(0,25), ipady=5)
        
        self.btn_frame = tk.Frame(container, bg=self.bg_color)
        self.btn_frame.pack(fill=tk.X)
        
        self.btn_start = tk.Button(self.btn_frame, text="START TRACKING", font=("Segoe UI", 10, "bold"), bg=self.accent_color, fg="#000000", activebackground="#00cc7a", relief=tk.FLAT, command=self.on_start)
        self.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10), ipady=5)
        
        self.btn_reset = tk.Button(self.btn_frame, text="CLEAR DATA", font=("Segoe UI", 10), bg="#ff4d4d", fg="#ffffff", activebackground="#cc0000", relief=tk.FLAT, command=self.on_reset)
        self.btn_reset.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=5)
        
        self.lbl_status = tk.Label(container, text="STATUS: WAITING FOR INPUT", bg=self.bg_color, fg="#888888", font=font_lbl, pady=25)
        self.lbl_status.pack(side=tk.BOTTOM)

    def ping_version(self):
        try:
            with open(os.path.join(DOCS_DIR, "version.json"), "w") as f:
                json.dump({"version": time.time()}, f)
        except:
            pass

    def on_start(self):
        u = self.var_username.get().strip()
        d = self.var_date.get().strip()
        p = self.var_preset.get().strip()
        
        if not u:
            messagebox.showerror("Error", "Username is required")
            return
            
        try:
            start_dt = datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid Date format. Use YYYY-MM-DD")
            return
            
        try:
            with open(PREFS_FILE, "w") as f:
                json.dump({"username": u, "start_date": d, "preset": p}, f)
        except:
            pass
            
        global TRACKER_STATE
        TRACKER_STATE["username"] = u
        TRACKER_STATE["start_date"] = start_dt
        self.ping_version()
        
        self.btn_start.pack_forget()
        self.btn_reset.pack_forget()
        
        self.btn_swap = tk.Button(self.btn_frame, text="UPDATE TRACKING", font=("Segoe UI", 10, "bold"), bg="#4da6ff", fg="#000000", activebackground="#1a8cff", relief=tk.FLAT, command=self.on_change_preset)
        self.btn_swap.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10), ipady=5)

        self.btn_stop = tk.Button(self.btn_frame, text="STOP & EXIT", font=("Segoe UI", 10, "bold"), bg="#ff4d4d", fg="#ffffff", activebackground="#cc0000", relief=tk.FLAT, command=self.on_stop)
        self.btn_stop.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=5)
        
        self.lbl_status.config(text=f"STATUS: TRACKING {u.upper()} | PORT {PORT}", fg=self.accent_color)
        
        preset_path = self.preset_files.get(p)
        global HTML_CONTENT
        if p != "Default (Built-in)" and preset_path and os.path.exists(preset_path):
            with open(preset_path, "r", encoding="utf-8") as f:
                HTML_CONTENT = f.read()

        cleanup_old_files(DOCS_DIR, RETENTION_DAYS)
        global EXPORT_THREAD_STARTED
        if not EXPORT_THREAD_STARTED:
            threading.Thread(target=export_loop, daemon=True).start()
            threading.Thread(target=run_server, daemon=True).start()
            EXPORT_THREAD_STARTED = True
        else:
            html_path = os.path.join(DOCS_DIR, "stats.html")
            try:
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(HTML_CONTENT)
            except:
                pass
        
    def on_change_preset(self):
        u = self.var_username.get().strip()
        d = self.var_date.get().strip()
        p = self.var_preset.get().strip()
        
        if not u:
            messagebox.showerror("Error", "Username is required")
            return
            
        try:
            start_dt = datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid Date format. Use YYYY-MM-DD")
            return

        global TRACKER_STATE
        TRACKER_STATE["username"] = u
        TRACKER_STATE["start_date"] = start_dt
        self.ping_version()
        
        preset_path = self.preset_files.get(p)
        global HTML_CONTENT
        if p != "Default (Built-in)" and preset_path and os.path.exists(preset_path):
            with open(preset_path, "r", encoding="utf-8") as f:
                HTML_CONTENT = f.read()
        else:
            HTML_CONTENT = self.default_html
            
        html_path = os.path.join(DOCS_DIR, "stats.html")
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(HTML_CONTENT)
            self.lbl_status.config(text=f"STATUS: TRACKING {u.upper()} | {p}", fg=self.accent_color)
            
            self.prefs["preset"] = p
            self.prefs["username"] = u
            self.prefs["start_date"] = d
            with open(PREFS_FILE, "w") as f:
                json.dump(self.prefs, f)
        except Exception as e:
            print("Error hot-swapping preset:", e)
        
    def on_reset(self):
        self.var_username.set("")
        self.var_date.set(datetime.now().strftime("%Y-%m-%d"))
        self.var_preset.set("Default (Built-in)")
        if os.path.exists(PREFS_FILE):
            os.remove(PREFS_FILE)
            self.lbl_status.config(text="STATUS: SAVED DATA CLEARED")

    def on_stop(self):
        self.root.destroy()
        os._exit(0)

def main():
    root = tk.Tk()
    app = StatsApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_stop)
    root.mainloop()

if __name__ == "__main__":
    main()
