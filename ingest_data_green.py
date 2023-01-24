#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
from time import time
from sqlalchemy import create_engine
import argparse

def main(params):
    user=params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'

    # download the csv
    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    df= next(df_iter)
    
    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    df.head(n=0).to_sql(name = table_name, con=engine, if_exists='replace')



    while True:
        t_start = time()
        #While loop to add each chunk to database. Will break from loop once no chunks left
        

        #Convert dates to datetime
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

        #Insert chunk in sql database
        df.to_sql(name = table_name, con=engine, if_exists='append')
        df = next(df_iter)
        t_end = time()

        print(f'inserted a chunk.....{t_end - t_start:.3f}')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', help='username for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table-name', help='name of the table where we will write the results too')
    parser.add_argument('--url', help='url of the csv file')

    args = parser.parse_args()

    main(args)





