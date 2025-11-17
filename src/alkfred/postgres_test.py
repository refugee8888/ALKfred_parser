
from dotenv import load_dotenv
from alkfred import config
import psycopg2 as pg


load_dotenv()
conn = config.postgres_conn()
cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())
cur.close()
conn.close()

