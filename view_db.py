import sqlite3, json

conn = sqlite3.connect('floraguard.db')
conn.row_factory = sqlite3.Row
rows = [dict(r) for r in conn.execute('SELECT * FROM sensor_telemetry ORDER BY id DESC LIMIT 10')]
print(json.dumps(rows, indent=2))
print(f"\nTotal records: {conn.execute('SELECT COUNT(*) FROM sensor_telemetry').fetchone()[0]}")
conn.close()

