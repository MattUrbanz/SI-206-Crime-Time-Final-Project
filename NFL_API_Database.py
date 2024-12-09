import json
import os
import sqlite3
from bs4 import BeautifulSoup
import requests
import http.client

cowboys_id = 6
lions_id = 8
patriots_id = 17
eagles_id = 21
steelers_id = 23
chargers_id = 24


DATABASE_NAME = "crime_tim_database.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)


id_list = [cowboys_id, lions_id, patriots_id, eagles_id, chargers_id]
team_list = ["Cowboys", "Lions", "Patriots", "Eagles", "Chargers"]


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


    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{str_year}/types/2/teams/{str_id}/record"
    response = requests.get(url)
    data = response.json()
    items = data.get("items", [])
    if items:
        summary = items[0].get("summary")
        if summary:
            overall_record = summary

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
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {team} (season INTEGER, wins INTEGER, losses INTEGER, key INTEGER)
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
    index = 0

    for index in range(0,5):
        query = f"SELECT COUNT(*) FROM {team_list[index]};"
        cur.execute(query)
        result = cur.fetchone()
        if result[0] == 0:
            for year in range(2000, 2025):
                data = get_season_record(id_list[index], year)
                team = team_list[index]

                cur.execute(f'''
                    INSERT INTO {team} (season, wins, losses, key) VALUES (?, ?, ?, ?)
                    ''', (year, data[0], data[1], 2))
            conn.commit()
            return

cnc = connect_database()
create_nfl_tables(cnc[0], cnc[1])
insert_nfl_data(cnc[0], cnc[1])