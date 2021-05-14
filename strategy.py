import datetime
import numpy as np
import pandas as pd
import psycopg2
import pandas.io.sql as psql


class Strategy:
    name = 'shadow catch'

    def __init__(self, logger):
        self.logger = logger

    def initdata(self, time: datetime.date) -> pd.DataFrame:
        pass


    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


def main():
        conn = psycopg2.connect(database="Crypto", user="postgres", password="123", host="195.248.242.36", port="5432")
        cur = conn.cursor()
        df = psql.read_sql("""Select * from "15m" where "symbol"='DOT/USDT' order by "timeStamp" desc limit 10""", conn)
        print(df)

if __name__ == '__main__':
        main()
