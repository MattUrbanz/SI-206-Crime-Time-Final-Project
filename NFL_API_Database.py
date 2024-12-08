import json
import os
import sqlite3
from bs4 import BeautifulSoup
import requests
import http.client


apikey = "34bf091696msh2d673e86a83d24cp1632f8jsnf9eb51390314"


cowboys_id = 6
lions_id = 8
rams_id = 14
patriots_id = 17
eagles_id = 21
steelers_id = 23
chargers_id = 24


DATABASE_NAME = "crime_time_database.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)


id_list = [cowboys_id, lions_id, rams_id, patriots_id, eagles_id, chargers_id]
team_list = ["Cowboys", "Lions", "Rams", "Patriots", "Eagles", "Chargers"]


def connect_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    return cur, conn


def get_season_record(id, year):
    '''
    Arguments:
        id: id number for football team whose record is desired to be extracted
        year: year of season which record is desired
    Returns:
        list of two integers, with the first integer being wins and second being losses
    Notes:
        None
    '''


    str_id = str(id)
    str_year = str(year)


    url = "https://nfl-api-data.p.rapidapi.com/nfl-team-record"


    querystring = {"id":f"{str_id}","year":f"{str_year}"}


    headers = {
        "x-rapidapi-key": apikey,
        "x-rapidapi-host": "nfl-api-data.p.rapidapi.com"
    }


    response = requests.get(url, headers=headers, params=querystring)
    response_data = response.json()


    overall_record = "0-0"


    for item in response_data.get('items', []):
        overall_record = item['summary']


    wl_lst = overall_record.split("-")
    wins = int(wl_lst[0])
    losses = int(wl_lst[1])
    wl = [wins, losses]
    return wl
   
def create_nfl_tables(cur, conn):
    '''
    Arguments
        cur: database cursor
        conn: database connection
   
    Returns
        none


    Notes
        Creates tables for storing NFL regular season data
    '''


    for team in team_list:
        cur.execute(f'DROP TABLE IF EXISTS {team}')
        cur.execute(f'''
            CREATE TABLE {team} (season INTEGER, wins INTEGER, losses INTEGER)
                    ''')
    conn.commit()


def insert_nfl_data(cur, conn):
    '''
    Arguments
        cur: database cursor
        conn: database connection
    Returns:
        None
    Notes
        Inserts data into databases for NFL teams including the Dallas Cowboys, Detroit Lions, Los Angeles Rams, New England Patriots,
        Philadelphia Eagles, and the Los Angeles Chargers. These databases include each teams win and loss counts for each season from
        the 2000 season up until the NFL's most recently concluded season, 2023.
    '''
    index = -1
    for id in id_list:
        index += 1
        for year in range(2000, 2023):
            data = get_season_record(id, year)
            team = team_list[index]
   
            cur.execute(f'''
                INSERT INTO {team} (season, wins, losses) VALUES (?, ?, ?)
                ''', (year, data[0], data[1]))
    conn.commit()


cnc = connect_database()
create_nfl_tables(cnc[0], cnc[1])
insert_nfl_data(cnc[0], cnc[1])
