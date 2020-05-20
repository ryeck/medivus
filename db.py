import psycopg2

host = "localhost"
database = "postgres"
user = "postgres"
password = "postgres"

conn = psycopg2.connect(host=host, database=database, user=user, password=password)

def insert(func):
  def wrapper(*args, **kwargs):
    try:
      cur = conn.cursor()
      cur.execute(func(*args, **kwargs))
      conn.commit()
      cur.close()
    except Exception as e:
      print(e) 
  return wrapper

def select(func):
  def wrapper(*args, **kwargs):
    try:
      cur = conn.cursor()
      cur.execute(func(*args, **kwargs))
      return cur.fetchall()
    except Exception as e:
      print(e) 
  return wrapper

def print_tables():
  cur = conn.cursor()
  cur.execute("SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';")
  for t in cur.fetchall():
    print(t)

@insert
def add_hunted(guild, name):
  return f"INSERT INTO hunted (guild, name) VALUES ({guild}, '{name}')"

@select
def get_hunted(guild):
  return f"SELECT name FROM hunted WHERE guild = {guild}"

if __name__ == "__main__":
  add_hunted(12345, "test")
