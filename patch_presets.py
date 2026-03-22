import os
import glob

CSS_INJECT = """
    <style>
        .floating-rating {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            color: white;
            padding: 10px 15px;
            border-radius: 12px;
            font-family: sans-serif;
            font-size: 14px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            z-index: 9999;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .rtg-val { font-weight: bold; color: #4da6ff; font-size: 18px; }
        .rtg-chg { font-size: 12px; padding: 2px 5px; border-radius: 4px; background: rgba(255,255,255,0.1); }
        .chg-pos { color: #00fa9a; text-shadow: 0 0 10px rgba(0,250,154,0.4); }
        .chg-neg { color: #ff4d4d; text-shadow: 0 0 10px rgba(255,77,77,0.4); }
    </style>
"""

HTML_INJECT = """
    <div class="floating-rating" id="floating-rating" style="display: none;">
        <span>Live Rating:</span>
        <span class="rtg-val" id="preset-rating">----</span>
        <span class="rtg-chg" id="preset-rating-change">0</span>
    </div>
"""

JS_INJECT = """
                if(data.length > 3 && data[3] > 0) {
                    let rtgDiv = document.getElementById("floating-rating");
                    if(rtgDiv) {
                        rtgDiv.style.display = "flex";
                        document.getElementById("preset-rating").textContent = data[3];
                        let chg = data[4] || 0;
                        let chgEl = document.getElementById("preset-rating-change");
                        chgEl.textContent = (chg > 0 ? "+" : "") + chg;
                        chgEl.className = "rtg-chg " + (chg > 0 ? "chg-pos" : (chg < 0 ? "chg-neg" : ""));
                    }
                }
"""

def patch():
    files = glob.glob("presetsHTML/*.html")
    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()

        if "floating-rating" in content:
            print(f"Skipping {fp} (already patched)")
            continue

        if "</head>" in content:
            content = content.replace("</head>", CSS_INJECT + "\n</head>")
        
        if "</body>" in content:
            content = content.replace("</body>", HTML_INJECT + "\n</body>")
        
        loc = content.find('const data = await res.json();')
        if loc == -1:
            loc = content.find('data = await res.json();')
        
        if loc != -1:
            # Find the position right after this line
            insert_pos = content.find(';', loc) + 1
            content = content[:insert_pos] + JS_INJECT + content[insert_pos:]
        
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched {fp}")

if __name__ == "__main__":
    patch()
