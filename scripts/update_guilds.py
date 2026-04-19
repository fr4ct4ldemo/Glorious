import sqlite3, sys
conn = sqlite3.connect('database.db')
rows = conn.execute('SELECT guild_id, COUNT(*) FROM accounts GROUP BY guild_id').fetchall()
print('Before:', rows)
non_zero = [r[0] for r in rows if r[0] != '0']
if not non_zero:
    print('No non-zero guilds found; aborting')
    sys.exit(0)
gid = non_zero[0]
conn.execute("UPDATE accounts SET guild_id = ? WHERE guild_id = '0' OR guild_id IS NULL", (gid,))
conn.commit()
print('Assigned 0 ->', gid)
print('After:', conn.execute('SELECT guild_id, COUNT(*) FROM accounts GROUP BY guild_id').fetchall())
conn.close()
