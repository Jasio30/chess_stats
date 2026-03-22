import os

files = {
"anime_cute_bubble.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Anime Cute</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;700&display=swap');
        body { background: transparent; padding: 20px; font-family: 'Fredoka', sans-serif; }
        .bubble { background: #fffafa; border: 4px solid #ffc0cb; border-radius: 30px; padding: 20px; display: inline-block; box-shadow: 0 10px 0 #ffc0cb; position: relative; }
        .header { color: #ff69b4; font-size: 14px; font-weight: bold; text-align: center; margin-bottom: 10px; }
        .stats-row { display: flex; gap: 15px; }
        .item { background: #fff; border-radius: 15px; padding: 10px 15px; text-align: center; border: 2px solid #ffebf0; }
        .val { font-size: 24px; font-weight: 700; color: #ff69b4; }
        .lbl { font-size: 10px; color: #ffb6c1; text-transform: uppercase; display: block; }
        .val-rating { color: #4da6ff; }
        .chg-val { font-size: 12px; margin-left: 2px; }
        .chg-pos { color: #00fa9a; }
        .chg-neg { color: #ff4d4d; }
    </style>
</head>
<body>
    <div class="bubble">
        <div class="header">Game Results ✨</div>
        <div class="stats-row">
            <div class="item"><span class="lbl">Wins</span><span id="wins" class="val">0</span></div>
            <div class="item"><span class="lbl">Draws</span><span id="draws" class="val">0</span></div>
            <div class="item"><span class="lbl">Losses</span><span id="losses" class="val">0</span></div>
            <div class="item"><span class="lbl">Rating</span><span id="rating" class="val val-rating">----</span><span id="rating-change" class="chg-val"></span></div>
        </div>
    </div>
    <script>
        async function updateStats() {
            try {
                const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
                const data = await res.json();
                document.getElementById("wins").textContent = data[0];
                document.getElementById("draws").textContent = data[1];
                document.getElementById("losses").textContent = data[2];
                if(data.length > 3 && data[3] > 0) {
                    document.getElementById("rating").textContent = data[3];
                    let chg = data[4] || 0;
                    let el = document.getElementById("rating-change");
                    el.textContent = chg > 0 ? "+" + chg : (chg < 0 ? chg : "");
                    el.className = "chg-val " + (chg > 0 ? "chg-pos" : "chg-neg");
                }
            } catch (e) { }
        }
        updateStats(); setInterval(updateStats, 5000);
    </script>
</body>
</html>""",

"cyberpunk_neon_edgy.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cyberpunk Neon</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
        body { background: #050505; color: #fff; font-family: 'Orbitron', sans-serif; padding: 20px; }
        .neon-panel { border: 2px solid #00f3ff; padding: 20px; background: rgba(0, 0, 0, 0.8); box-shadow: 0 0 15px #00f3ff, inset 0 0 5px #00f3ff; position: relative; overflow: hidden; clip-path: polygon(0% 0%, 100% 0%, 100% 85%, 95% 100%, 0% 100%); }
        .glitch-text { font-size: 14px; color: #ff0055; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 15px; display: block; }
        .stat-grid { display: flex; gap: 30px; }
        .stat { flex: 1; }
        .label { font-size: 10px; color: #00f3ff; display: block; margin-top: 5px; }
        .value { font-size: 36px; font-weight: 900; text-shadow: 2px 2px #ff0055; }
        .win-val { color: #00ffaa; text-shadow: 0 0 10px #00ffaa; }
        .loss-val { color: #ff0055; text-shadow: 0 0 10px #ff0055; }
        .rating-val { color: #00f3ff; text-shadow: 0 0 10px #00f3ff; }
        .chg-val { font-size: 14px; margin-left:8px; vertical-align: middle;}
        .chg-pos { color: #00ffaa; text-shadow: none; }
        .chg-neg { color: #ff0055; text-shadow: none; }
    </style>
</head>
<body>
    <div class="neon-panel">
        <span class="glitch-text">Session // Active</span>
        <div class="stat-grid">
            <div class="stat"><div id="wins" class="value win-val">0</div><span class="label">WINS</span></div>
            <div class="stat"><div id="draws" class="value">0</div><span class="label">DRAWS</span></div>
            <div class="stat"><div id="losses" class="value loss-val">0</div><span class="label">LOSSES</span></div>
            <div class="stat"><div class="value rating-val"><span id="rating">----</span><span id="rating-change" class="chg-val"></span></div><span class="label">RATING</span></div>
        </div>
    </div>
    <script>
        async function updateStats() {
            try {
                const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
                const data = await res.json();
                document.getElementById("wins").textContent = data[0];
                document.getElementById("draws").textContent = data[1];
                document.getElementById("losses").textContent = data[2];
                if(data.length > 3 && data[3] > 0) {
                    document.getElementById("rating").textContent = data[3];
                    let chg = data[4] || 0;
                    let el = document.getElementById("rating-change");
                    el.textContent = chg > 0 ? "[+" + chg + "]" : (chg < 0 ? "[" + chg + "]" : "");
                    el.className = "chg-val " + (chg > 0 ? "chg-pos" : "chg-neg");
                }
            } catch (e) { }
        }
        updateStats(); setInterval(updateStats, 5000);
    </script>
</body>
</html>""",

"minimalist_light_apple.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Minimalist Light</title>
    <style>
        body { background: white; color: #1d1d1f; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Arial, sans-serif; padding: 20px; display: flex; }
        .container { background: #f5f5f7; border-radius: 18px; padding: 12px 24px; display: flex; align-items: center; gap: 32px; }
        .stat { display: flex; flex-direction: column; align-items: center; }
        .value { font-size: 24px; font-weight: 600; }
        .label { font-size: 11px; color: #86868b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
        .dot { width: 4px; height: 4px; border-radius: 2px; background: #d2d2d7; }
        .rtg-val { color: #0066cc; }
        .chg { font-size: 12px; margin-left: 4px; font-weight: bold;}
        .chg-pos { color: #34c759; }
        .chg-neg { color: #ff3b30; }
    </style>
</head>
<body>
    <div class="container">
        <div class="stat"><span class="label">Wins</span><span id="wins" class="value">0</span></div>
        <div class="dot"></div>
        <div class="stat"><span class="label">Draws</span><span id="draws" class="value">0</span></div>
        <div class="dot"></div>
        <div class="stat"><span class="label">Losses</span><span id="losses" class="value">0</span></div>
        <div class="dot"></div>
        <div class="stat"><span class="label">Rating</span><span class="value rtg-val"><span id="rating">----</span><span id="rating-change" class="chg"></span></span></div>
    </div>
    <script>
        async function updateStats() {
            try {
                const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
                const data = await res.json();
                document.getElementById("wins").textContent = data[0];
                document.getElementById("draws").textContent = data[1];
                document.getElementById("losses").textContent = data[2];
                if(data.length > 3 && data[3] > 0) {
                    document.getElementById("rating").textContent = data[3];
                    let chg = data[4] || 0;
                    let el = document.getElementById("rating-change");
                    el.textContent = chg > 0 ? "↑" + chg : (chg < 0 ? "↓" + Math.abs(chg) : "");
                    el.className = "chg " + (chg > 0 ? "chg-pos" : "chg-neg");
                }
            } catch (e) { }
        }
        updateStats(); setInterval(updateStats, 5000);
    </script>
</body>
</html>""",

"modern_dark_card.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Modern Card</title>
    <style>
        body { background: #121212; color: #e0e0e0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; display: flex; padding: 20px; }
        .card { background: #1e1e1e; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); display: flex; gap: 24px; align-items: center; }
        .stat-box { text-align: center; }
        .val { font-size: 28px; font-weight: bold; display: block; }
        .label { font-size: 12px; color: #888; text-transform: uppercase; }
        .win { color: #4CAF50; }
        .draw { color: #FFC107; }
        .loss { color: #F44336; }
        .rtg { color: #2196F3; }
        .divider { width: 1px; height: 40px; background: #333; }
        .chg { font-size: 14px; margin-left: 2px;}
        .chg-pos { color: #4CAF50; }
        .chg-neg { color: #F44336; }
    </style>
</head>
<body>
    <div class="card">
        <div class="stat-box"><span class="label">Wins</span><span id="wins" class="val win">0</span></div>
        <div class="divider"></div>
        <div class="stat-box"><span class="label">Draws</span><span id="draws" class="val draw">0</span></div>
        <div class="divider"></div>
        <div class="stat-box"><span class="label">Losses</span><span id="losses" class="val loss">0</span></div>
        <div class="divider"></div>
        <div class="stat-box"><span class="label">Rating</span><span class="val rtg"><span id="rating">----</span><span id="rating-change" class="chg"></span></span></div>
    </div>
    <script>
        async function updateStats() {
            try {
                const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
                const data = await res.json();
                document.getElementById("wins").textContent = data[0];
                document.getElementById("draws").textContent = data[1];
                document.getElementById("losses").textContent = data[2];
                if(data.length > 3 && data[3] > 0) {
                    document.getElementById("rating").textContent = data[3];
                    let chg = data[4] || 0;
                    let el = document.getElementById("rating-change");
                    el.textContent = chg > 0 ? "+" + chg : (chg < 0 ? chg : "");
                    el.className = "chg " + (chg > 0 ? "chg-pos" : "chg-neg");
                }
            } catch (e) { }
        }
        updateStats(); setInterval(updateStats, 5000);
    </script>
</body>
</html>""",

"plain_text_minimalist.html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Plain Stats</title>
  <style>
    body { font-size: 48px; font-weight: bold; font-family: sans-serif; }
    small { font-size: 18px; font-weight: normal; color: #666; }
    .rtg { color: #0066cc; }
    .chg-pos { color: green; }
    .chg-neg { color: red; }
  </style>
</head>
<body>
  W: <span id="wins">0</span> | D: <span id="draws">0</span> | L: <span id="losses">0</span> | R: <span id="rating" class="rtg">----</span> <small id="rating-change"></small>
  <br>
  <small>Updated: <span id="updated">--</span></small>
  <script>
    async function updateStats() {
      try {
        const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
        const data = await res.json();
        document.getElementById("wins").textContent = data[0];
        document.getElementById("draws").textContent = data[1];
        document.getElementById("losses").textContent = data[2];
        document.getElementById("updated").textContent = new Date().toLocaleTimeString();
        if(data.length > 3 && data[3] > 0) {
            document.getElementById("rating").textContent = data[3];
            let chg = data[4] || 0;
            let el = document.getElementById("rating-change");
            el.textContent = chg > 0 ? "(+" + chg + ")" : (chg < 0 ? "(" + chg + ")" : "");
            el.className = chg > 0 ? "chg-pos" : "chg-neg";
        }
      } catch (e) {}
    }
    updateStats(); setInterval(updateStats, 5000);
  </script>
</body>
</html>""",

"premium_glass_overlay.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Premium Glass</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background: transparent; margin: 0; padding: 20px; font-family: 'Outfit', sans-serif; color: white; }
        .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 30px; display: inline-grid; grid-template-columns: repeat(4, 1fr); gap: 30px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); }
        .item { text-align: center; }
        .count { font-size: 48px; font-weight: 700; display: block; margin-bottom: 5px; }
        .label { font-size: 12px; letter-spacing: 2px; text-transform: uppercase; opacity: 0.6; }
        .w { color: #00ffaa; text-shadow: 0 0 20px rgba(0, 255, 170, 0.4); }
        .d { color: #ffdd44; text-shadow: 0 0 20px rgba(255, 221, 68, 0.4); }
        .l { color: #ff4466; text-shadow: 0 0 20px rgba(255, 68, 102, 0.4); }
        .r { color: #4da6ff; text-shadow: 0 0 20px rgba(77, 166, 255, 0.4); }
        .footer { grid-column: span 4; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 15px; font-size: 10px; opacity: 0.5; text-align: right; }
        .chg-val { font-size: 16px; margin-left: 5px; vertical-align: top;}
        .chg-pos { color: #00ffaa; text-shadow: none;}
        .chg-neg { color: #ff4466; text-shadow: none;}
    </style>
</head>
<body>
    <div class="glass">
        <div class="item"><span id="wins" class="count w">0</span><span class="label">Wins</span></div>
        <div class="item"><span id="draws" class="count d">0</span><span class="label">Draws</span></div>
        <div class="item"><span id="losses" class="count l">0</span><span class="label">Losses</span></div>
        <div class="item"><span class="count r"><span id="rating">----</span><span id="rating-change" class="chg-val"></span></span><span class="label">Live Rating</span></div>
        <div class="footer">LIVE SERVER SYNC ACTIVE // <span id="updated">--:--:--</span></div>
    </div>
    <script>
        async function updateStats() {
            try {
                const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
                const data = await res.json();
                document.getElementById("wins").textContent = data[0];
                document.getElementById("draws").textContent = data[1];
                document.getElementById("losses").textContent = data[2];
                document.getElementById("updated").textContent = new Date().toLocaleTimeString();
                if(data.length > 3 && data[3] > 0) {
                    document.getElementById("rating").textContent = data[3];
                    let chg = data[4] || 0;
                    let el = document.getElementById("rating-change");
                    el.textContent = chg > 0 ? "+" + chg : (chg < 0 ? chg : "");
                    el.className = "chg-val " + (chg > 0 ? "chg-pos" : "chg-neg");
                }
            } catch (e) { }
        }
        updateStats(); setInterval(updateStats, 5000);
    </script>
</body>
</html>""",

"retro_terminal_simple.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Retro Terminal</title>
    <style>
        body { background: #000; color: #00ff00; font-family: 'Courier New', Courier, monospace; padding: 20px; text-transform: uppercase; }
        .container { border: 1px solid #00ff00; display: inline-block; padding: 15px; }
        .stat { margin: 5px 0; }
        .cursor { animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0; } }
        .rtg { color: #00ffff; font-weight:bold; }
    </style>
</head>
<body>
    <div class="container">
        <div>> SYSTEM_STATS_LOADED</div>
        <div class="stat">WINS....[<span id="wins">0</span>]</div>
        <div class="stat">DRAWS...[<span id="draws">0</span>]</div>
        <div class="stat">LOSSES..[<span id="losses">0</span>]</div>
        <div class="stat">RATING..[<span id="rating" class="rtg">----</span><span id="rating-change"></span>]</div>
        <div style="margin-top: 10px; font-size: 0.8em; color: #008800;">
            LAST_SYNC: <span id="updated">--</span><span class="cursor">_</span>
        </div>
    </div>
    <script>
        async function updateStats() {
            try {
                const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
                const data = await res.json();
                document.getElementById("wins").textContent = data[0].toString().padStart(3, '0');
                document.getElementById("draws").textContent = data[1].toString().padStart(3, '0');
                document.getElementById("losses").textContent = data[2].toString().padStart(3, '0');
                document.getElementById("updated").textContent = new Date().toLocaleTimeString();
                if(data.length > 3 && data[3] > 0) {
                    document.getElementById("rating").textContent = data[3];
                    let chg = data[4] || 0;
                    document.getElementById("rating-change").textContent = chg > 0 ? " (+" + chg + ")" : (chg < 0 ? " (" + chg + ")" : "");
                }
            } catch (e) { }
        }
        updateStats(); setInterval(updateStats, 5000);
    </script>
</body>
</html>""",

"streamer_overlay_horizontal.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Streamer Overlay Wide</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@800&display=swap');
        body { background: transparent; margin: 0; padding: 10px; font-family: 'Kanit', sans-serif; }
        .stream-bar { background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(10px); border-left: 5px solid #ff00ff; display: flex; align-items: center; color: white; padding: 0 20px; height: 50px; border-radius: 4px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5); }
        .title { color: #ff00ff; font-size: 14px; margin-right: 20px; text-transform: uppercase; letter-spacing: 2px; }
        .stats { display: flex; gap: 20px; font-size: 20px; align-items: center;}
        .s-win { color: #00ffaa; }
        .s-draw { color: #ffff00; }
        .s-loss { color: #ff4444; }
        .s-rtg { color: #00ffff; }
        .sep { color: rgba(255, 255, 255, 0.2); }
        .chg-pos { color: #00ffaa; font-size: 14px; }
        .chg-neg { color: #ff4444; font-size: 14px; }
    </style>
</head>
<body>
    <div class="stream-bar">
        <div class="title">Session Record</div>
        <div class="stats">
            <span class="s-win">W: <span id="wins">0</span></span><span class="sep">/</span>
            <span class="s-draw">D: <span id="draws">0</span></span><span class="sep">/</span>
            <span class="s-loss">L: <span id="losses">0</span></span><span class="sep">/</span>
            <span class="s-rtg">R: <span id="rating">----</span> <span id="rating-change"></span></span>
        </div>
    </div>
    <script>
        async function updateStats() {
            try {
                const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
                const data = await res.json();
                document.getElementById("wins").textContent = data[0];
                document.getElementById("draws").textContent = data[1];
                document.getElementById("losses").textContent = data[2];
                if(data.length > 3 && data[3] > 0) {
                    document.getElementById("rating").textContent = data[3];
                    let chg = data[4] || 0;
                    let el = document.getElementById("rating-change");
                    el.textContent = chg > 0 ? "+" + chg : (chg < 0 ? chg : "");
                    el.className = chg > 0 ? "chg-pos" : "chg-neg";
                }
            } catch (e) { }
        }
        updateStats(); setInterval(updateStats, 5000);
    </script>
</body>
</html>""",

"vibrant_gradient_bold.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Vibrant Gradient</title>
    <style>
        body { background: transparent; margin: 0; padding: 20px; font-family: 'Segoe UI', sans-serif; }
        .container { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2px; border-radius: 20px; display: inline-block; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); }
        .inner { background: #111; border-radius: 18px; padding: 25px; display: flex; flex-direction: column; gap: 15px; }
        .stat { display: flex; justify-content: space-between; gap: 40px; align-items: center; }
        .name { color: #aaa; font-size: 14px; font-weight: bold; text-transform: uppercase; }
        .num { color: #fff; font-size: 32px; font-weight: 800; }
        .win-num { color: #00ffcc; text-shadow: 0 0 10px rgba(0, 255, 204, 0.3); }
        .loss-num { color: #ff5e62; text-shadow: 0 0 10px rgba(255, 94, 98, 0.3); }
        .rtg-num { color: #66ccff; text-shadow: 0 0 10px rgba(102, 204, 255, 0.3); }
        .chg-val { font-size: 14px; margin-left:8px; vertical-align: middle;}
        .chg-pos { color: #00ffcc; text-shadow: none; }
        .chg-neg { color: #ff5e62; text-shadow: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="inner">
            <div class="stat"><span class="name">Victory</span><span id="wins" class="num win-num">0</span></div>
            <div class="stat"><span class="name">Draw</span><span id="draws" class="num">0</span></div>
            <div class="stat"><span class="name">Defeat</span><span id="losses" class="num loss-num">0</span></div>
            <div class="stat"><span class="name">Rating</span><span class="num rtg-num"><span id="rating">----</span><span id="rating-change" class="chg-val"></span></span></div>
        </div>
    </div>
    <script>
        async function updateStats() {
            try {
                const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
                const data = await res.json();
                document.getElementById("wins").textContent = data[0];
                document.getElementById("draws").textContent = data[1];
                document.getElementById("losses").textContent = data[2];
                if(data.length > 3 && data[3] > 0) {
                    document.getElementById("rating").textContent = data[3];
                    let chg = data[4] || 0;
                    let el = document.getElementById("rating-change");
                    el.textContent = chg > 0 ? "(+" + chg + ")" : (chg < 0 ? "(" + chg + ")" : "");
                    el.className = "chg-val " + (chg > 0 ? "chg-pos" : "chg-neg");
                }
            } catch (e) { }
        }
        updateStats(); setInterval(updateStats, 5000);
    </script>
</body>
</html>""",

"wooden_classic_board.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wooden Classic</title>
    <style>
        body { background: transparent; padding: 20px; font-family: 'Georgia', serif; }
        .board-frame { background: #5d4037; border: 4px solid #3e2723; border-radius: 8px; padding: 10px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4); display: inline-block; }
        .inner-stats { background: #efebe9; border: 2px solid #d7ccc8; padding: 15px; display: flex; gap: 20px; }
        .stat { text-align: center; min-width: 60px; }
        .label { display: block; font-size: 12px; color: #795548; font-style: italic; margin-bottom: 5px; border-bottom: 1px solid #d7ccc8; }
        .value { font-size: 28px; font-weight: bold; color: #3e2723; }
        .rtg-val { color: #1a237e; }
        .chg-val { font-size: 14px; font-weight: normal;}
    </style>
</head>
<body>
    <div class="board-frame">
        <div class="inner-stats">
            <div class="stat"><span class="label">Won</span><span id="wins" class="value">0</span></div>
            <div class="stat"><span class="label">Drawn</span><span id="draws" class="value">0</span></div>
            <div class="stat"><span class="label">Lost</span><span id="losses" class="value">0</span></div>
            <div class="stat"><span class="label">Rating</span><span class="value rtg-val"><span id="rating">----</span> <span id="rating-change" class="chg-val"></span></span></div>
        </div>
    </div>
    <script>
        async function updateStats() {
            try {
                const res = await fetch("/summary_stats.json?_=" + new Date().getTime());
                const data = await res.json();
                document.getElementById("wins").textContent = data[0];
                document.getElementById("draws").textContent = data[1];
                document.getElementById("losses").textContent = data[2];
                if(data.length > 3 && data[3] > 0) {
                    document.getElementById("rating").textContent = data[3];
                    let chg = data[4] || 0;
                    let el = document.getElementById("rating-change");
                    el.textContent = chg > 0 ? "+" + chg : (chg < 0 ? chg : "");
                    el.style.color = chg > 0 ? "#2e7d32" : "#c62828";
                }
            } catch (e) { }
        }
        updateStats(); setInterval(updateStats, 5000);
    </script>
</body>
</html>"""
}

def rebuild():
    for name, content in files.items():
        with open(os.path.join("presetsHTML", name), "w", encoding="utf-8") as f:
            f.write(content)
        print("Rebuilt", name)

if __name__ == "__main__":
    rebuild()
