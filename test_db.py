import sys

sys.path.append('src')
from thermoneural.storage.db import save_run

save_run({'failure_mode': 'Test', 'confidence': '95%', 'total_risk': '$100'})
import sqlite3

c = sqlite3.connect('history.db')
print(c.execute('SELECT * FROM runs').fetchall())
