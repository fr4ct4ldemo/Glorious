import sqlite3, asyncio, importlib, sys

conn = sqlite3.connect('database.db')
row = conn.execute("SELECT guild_id FROM accounts WHERE guild_id != '0' LIMIT 1").fetchone()
if not row:
    print('No non-zero guilds found; aborting')
    sys.exit(0)
gid = row[0]
print('Selected guild:', gid)
print('Per-service counts:', conn.execute('SELECT service_name, COUNT(*) FROM accounts WHERE guild_id = ? GROUP BY service_name', (gid,)).fetchall())
conn.close()

# import glorious and run build_stock_embed
g = importlib.import_module('glorious')
async def main():
    emb = await g.build_stock_embed(gid, None)
    print('Embed title:', emb.title)
    print('Embed description:\n', emb.description)

asyncio.run(main())
