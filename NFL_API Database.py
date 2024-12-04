import requests
import json
import unittest
import os
import re
import sqlite3
import http.client

apikey = "4mUliNsMpBI4C0LiWapMSFLJhGVdXSVbVocFdU7Z"

cowboys_id = 6
lions_id = 8
rams_id = 14
patriots_id = 17
eagles_id = 21
steelers_id = 23
chargers_id = 24

id_list = [cowboys_id, lions_id, rams_id, patriots_id, eagles_id, chargers_id]
team_list = ["Cowboys", "Lions", "Rams", "Patriots", "Eagles", "Chargers"]

def get_team_record(id, year):
    '''
    Arguments
        id: integer of the team id whose record is being returned
        year: the season in which the team record is being returned

    Returns
        A string of the record of the specified team for the specified season in the format wins-losses

    Notes
        None
    '''

    str_id = str(id)
    str_year = str(year)

    conn = http.client.HTTPSConnection("nfl-api-data.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': apikey,
        'x-rapidapi-host': "nfl-api-data.p.rapidapi.com"
    }

    conn.request("GET", f"/nfl-team-record?id={str_id}&year={str_year}", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Parse the JSON response
    data_json = json.loads(data.decode("utf-8"))

    # Extract the "summary" key from the response
    if "items" in data_json and len(data_json["items"]) > 0:
        # For example, extracting the "summary" from the first item
        summary = data_json["items"][0].get("summary", "No summary found")
        return(summary)
    else:
        return "No data available for the given parameters"
    
def get_wins_and_losses(record):
    '''
    Arguments
        record: string of wins-loses for a single nfl team in a season
    Returns
        list of two integers, with the first integer being wins and second being losses

    Notes
        None
    '''
    wl_lst = record.split("-")
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
        cur.execute('DROP TABLE IF EXISTS ?', (team,))
        cur.execute('''
                    CREATE TABLE ? (season INTEGER, wins INTEGER, losses INTEGER)
                    ''')
    conn.commit()
    conn.close()

def insert_nfl_data(season, win_amount, loss_amount, cur, conn, team):
    cur.execute('''
                INSERT INTO ? (season, wins, losses) VALUES ?, ?, ?
                ''', (team, season, win_amount, loss_amount))
    conn.commit()
    conn.close()

def make_nfl_tables(cur, conn):
    '''
    Arguments
        cur: database cursor
        conn: database connection

    Returns
        None

    Notes
        Creates database for NFL teams including the Dallas Cowboys, Detroit Lions, Los Angeles Rams, New England Patriots, 
        Philadelphia Eagles, and the Los Angeles Chargers. This database includes each teams win and loss counts for each season from 
        the 2000 season up until the NFL's most recently concluded season, 2023.
    '''

    #Making tables for teams
    create_nfl_tables(cur,conn)

    #Putting team data into database
    index = -1
    for id in id_list:
        year = 2000
        index += 1
        while year <= 2023:
            record = get_team_record(id, year)
            wl = get_wins_and_losses(record)
            insert_nfl_data(year, wl[0], wl[1], cur, conn, team_list[index])
            year += 1