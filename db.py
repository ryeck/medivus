import psycopg2

host = "localhost"
database = "postgres"
user = "postgres"
password = "postgres"

conn = psycopg2.connect(host=host, database=database, user=user, password=password)

def update(func):
  def wrapper(*args, **kwargs):
    try:
      cur = conn.cursor()
      query, args = func(*args, **kwargs)
      cur.execute(query, args)
      conn.commit()
      cur.close()
      if cur.rowcount > 0:
        return True
      else:
        return False
    except Exception as e:
      # add log error
      print(e) 
      return None 
  return wrapper

def select(func):
  def wrapper(*args, **kwargs):
    try:
      cur = conn.cursor()
      query, args = func(*args, **kwargs)
      cur.execute(query, args)
      return cur.fetchall()
    except Exception as e:
      print(e) 
  return wrapper

def print_tables():
  cur = conn.cursor()
  cur.execute("SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';")
  for t in cur.fetchall():
    print(t)


# hunted list
@update
def add_hunted(guild, name):
  return "INSERT INTO hunted (guild, name) VALUES (%s, LOWER(%s)) ON CONFLICT DO NOTHING", (guild, name)

@update
def remove_hunted(guild, name):
  return "DELETE FROM hunted WHERE guild = %s and name = %s", (guild, name)

@select
def get_hunted(guild):
  return f"SELECT name FROM hunted WHERE guild = %s", (guild,)

@select
def get_all_hunted():
  return f"SELECT name, guild FROM hunted"


# team list
@update
def add_team(guild, name):
  return "INSERT INTO team (guild, name) VALUES (%s, LOWER(%s)) ON CONFLICT DO NOTHING", (guild, name)

@update
def remove_team(guild, name):
  return "DELETE FROM team WHERE guild = %s and name = %s", (guild, name)

@select
def get_team(guild):
  return "SELECT name FROM team WHERE guild = %s", (guild,)

@select
def get_all_team():
  return f"SELECT name, guild FROM team"


# noob list
@update
def add_noob(guild, name):
  return "INSERT INTO noob (guild, name) VALUES (%s, LOWER(%s)) ON CONFLICT DO NOTHING", (guild, name)

@update
def remove_noob(guild, name):
  return "DELETE FROM noob WHERE guild = %s and name = %s", (guild, name)

@select
def get_noob(guild):
  return "SELECT name FROM noob WHERE guild = %s", (guild,)

@select
def get_all_noob():
  return f"SELECT name, guild FROM noob"


# spawn list
@update
def add_spawn(guild, name):
  return "INSERT INTO spawn (guild, name) VALUES (%s, LOWER(%s)) ON CONFLICT DO NOTHING", (guild, name)

@update
def remove_spawn(guild, name):
  return "DELETE FROM spawn WHERE guild = %s and name = %s", (guild, name)

@select
def get_spawn(guild):
  return "SELECT spawn FROM spawn WHERE guild = %s", (guild,)

@select
def get_all_spawn():
  return f"SELECT name, guild FROM spawn"


# login
@update
def add_login(name, date):
  return "INSERT INTO login (name, date) VALUES (%s, %s)", (name, date)


# logoff
@update
def add_logoff(name, date):
  return "INSERT into logoff (name, date) VALUES (%s, %s)", (name, date)







if __name__ == "__main__":
  pass
