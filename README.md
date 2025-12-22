# ♟️ ChessStats Live Overlay

A lightweight, efficient Python-based live tracking system for Chess.com game statistics. Designed to be used as a source for OBS/streaming software or as a personal performance dashboard.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Chess.com](https://img.shields.io/badge/API-Chess.com-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Overview

ChessStats monitors a player's performance from a specified starting date, aggregating wins, draws, and losses. Unlike simple scrapers, it features **historical caching** to optimize API usage and prevent rate-limiting while providing a **live-updating web interface**.

## ✨ Key Features

- **Smart Caching:** Identifies "closed" months and caches them locally, ensuring only the current month is polled for updates.
- **Embedded Web Server:** Automatically spins up a local server (`localhost:8001`) to serve a clean, glassmorphism-inspired overlay.
- **Automated Cleanup:** Manages the `Documents/ChessStats` storage folder by automatically archiving/deleting logs older than 30 days.
- **Stream-Ready:** The output is a transparent, high-contrast HTML page perfectly suited for OBS Browser Sources.
- **Robust Error Handling:** Built-in protection against API downtime and malformed data.

## 🛠️ Installation

### 1. Prerequisite
Ensure you have Python 3.8 or higher installed on your system.

### 2. Install Dependencies
This project utilizes the official `chess.com` wrapper:

```bash
pip install chessdotcom
```

### 3. File Structure
The script stores all configuration and temporary files in a dedicated folder:
`C:/Users/<User>/Documents/ChessStats`

## 📖 Usage

1. **Run the script:**
   ```bash
   python chess_stats.py
   ```
2. **Configuration:**
   - Enter your **Chess.com username**.
   - Enter the **Start Date** (Format: `YYYY-MM-DD`). The script will begin calculating your record from this date forward.
3. **View Stats:**
   - Your browser will automatically open `http://localhost:8001/stats.html`.
   - In **OBS**, add a new **Browser Source** and point it to the URL above. Set the background to transparent if desired.

## ⚙️ Configuration

You can modify the constants at the top of `chess_stats.py` to customize the behavior:

| Constant | Description | Default |
| :--- | :--- | :--- |
| `PORT` | The port for the local web server | `8001` |
| `INTERVAL_SECONDS` | How often to poll for new games | `5` |
| `RETENTION_DAYS` | How long to keep temporary logs | `30` |

## 🧩 Architecture

- **Backend:** Python + `threading`. The main thread manages the HTTP server while a background daemon handles iterative API polling.
- **Frontend:** Vanilla JS + HTML5. Uses the `fetch` API for zero-dependency live updates.
- **Data Persistence:** JSON-based local storage.

## ⚖️ License & Disclaimer

This project is licensed under the MIT License. It is not affiliated with, maintained, or endorsed by Chess.com. Please ensure your `User-Agent` includes a valid email address as per Chess.com API guidelines.

---
*Created by [Jasio30/GitHub]*
