import sqlite3
import pandas as pd

with sqlite3.connect('/Users/edy/byt_pub/a_songbo/vn/data/options_data.db') as conn:
    df = pd.read_sql('SELECT * FROM options_imp', conn)

    # df.to_sql('stocks',conn,if_exists='append', index=False)
    print(df)

