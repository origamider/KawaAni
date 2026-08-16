import sqlite3
import pandas as pd


# conn = connect("../data/test.db")
# cur = conn.cursor()
# df = pd.read_csv('../data/anime_cleaned.csv')
# df.to_sql('anime_cleaned', conn, if_exists='replace')

conn = sqlite3.connect('../data/test.db')
df = pd.read_sql("select title_japanese from anime_cleaned order by score desc", conn)
print(df[:10])