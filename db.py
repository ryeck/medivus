import psycopg2

host = "localhost"
database = "db"
user = "postgres"
password = "postgres"

conn = psycopg2.connect(host=host, database=database, user=user, password=password)
cur = conn.cursor()
cur.execute("SELECT version()")
print(cur.fetchone())



