
from alkfred import config



conn = config.postgres_conn()
cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())
cur.close()
conn.close()

