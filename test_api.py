import os
import sys
from datetime import datetime
from chess_stats import get_month_stats

try:
    start = datetime(2024, 5, 1)
    # Test for hikaru in May 2024
    res = get_month_stats("hikaru", 2024, 5, start)
    print("TEST RESULT:", res)
    sys.exit(0 if res["success"] else 1)
except Exception as e:
    print("ERROR:", e)
    sys.exit(1)
