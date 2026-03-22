# Chess.com Live Stats OBS Tracker

![App Icon](icon.ico)

A lightweight, high-performance Python application that tracks Chess.com player statistics and natively hosts beautiful, auto-refreshing UI presets for live streaming via OBS Studio. The app features completely separate Thread architecture allowing zero-downtime hot swapping of players and layouts.

## Features

- **Live Leaderboard Tracking**: Streams Win/Draw/Loss and Rating shifts directly from the Chess.com unified API.
- **Auto-Refresh Core**: Emits a `location.reload()` DOM signal to all connected dashboards the second you change a setting, eliminating the need to ever manually refresh OBS sources.
- **Zero-Downtime Hot Swapping**: Switch current tracking user, start date, or visual preset directly from the Setup panel mid-stream without terminating server threads or tracking loops.
- **OBS High-DPI Vector Scaling**: The Chromium engine automatically enlarges and crisply scales all vector fonts and UI elements natively (2.5x base resolution) preventing OBS source pixelation.
- **Immersive Dark Config**: Features a custom-rendered `Tkinter` application frame wrapped in native Windows 11 Dark Mode DWM logic and a high-resolution logo.
- **15+ Custom Web Presets**: Select from over 15 dynamically patched HTML themes including:
  - `Cyberpunk Neon Edgy`
  - `Retro Terminal Simple`
  - `Synthwave 80s Grid`
  - `Minimalist Dark Obs` (Perfect for transparent overlays!)
  - *...and many more!*

## Prerequisites

- Python 3.8+
- `pip install requests`

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/Jasio30/chess_stats.git
   cd chess_stats
   ```
2. Run the application:
   ```bash
   python chess_stats.py
   ```

## How to setup as an OBS Overlay

1. Launch `chess_stats.py` to open the Configurator GUI.
2. Enter your **Chess.com Username** and the **Start Date** to track from.
3. Select an aesthetic preset from the dropdown menu and click **START TRACKING**.
4. The background server starts locally on your computer. Open **OBS Studio**.
5. Add a new **Browser Source**.
6. Set the URL to: `http://localhost:8001/stats.html`
7. Set the Width and Height to roughly `600x200` (adjust as needed; presets natively zoom 250% for crispness).
8. Feel free to Hot-Swap presets in the GUI! OBS will automatically reload the new styles seamlessly!

## Preferences

The application natively generates a folder in your `Documents/ChessStats` directory containing the active `stats.html` broadcast payload and caching your API progress to ensure you never get rate-limited. It also saves your `user_prefs.json` so you don't have to re-type your layout the next time you boot.

## License

This project is open-source and available under the [MIT License](LICENSE).
