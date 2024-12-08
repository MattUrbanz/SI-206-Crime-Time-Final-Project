import json
import os
import sqlite3
from bs4 import BeautifulSoup
import requests

#Create the MLB Databases
DATABASE_NAME = 'crime_time_database.db'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
def connect_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    return conn, cur

def create_mlb_tables(cur,conn, team):
    '''
    Arguments
        cur: databse cursor 
        conn: database connection
    Returns
        None
    Notes:
        Creates table for storing MLB regular season data
    '''

    
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS {team} (season INTEGER, wins INTEGER, losses INTEGER)
                ''')
    conn.commit()

def insert_mlb_data(year, win_amount, loss_amount, cur, conn, team):
    '''
    Arguments
        cur: databse cursor 
        conn: database connection
        season: Integer
        win_amount: Integer
        loss_amount: Integer

    Returns
        None
    Notes:
        Inserts record for each regular season past 2000 into database
    '''
    cur.execute(f'''
        INSERT INTO {team} (season, wins, losses) VALUES ({year}, {win_amount}, {loss_amount})
                ''')
    conn.commit()

teams = {'DET' : 'Detroit_Tigers', 'TEX' : 'Texas_Rangers', 'BOS' : 'Boston_Red_Sox', 'LAD' : 'Los_Angeles_Dodgers', 'PHI' : 'Philladelphia_Phillies'}
team_abbs = teams.keys()

for team_abb in team_abbs:
    url = 'https://www.baseball-reference.com/teams/' + team_abb + '/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    print(r.status_code)
    table = soup.find('tbody')
    
    
    table_headers = soup.find_all('th', attrs = {'data-stat': 'year_ID', 'class': 'left'})
    

    for header in table_headers:
        a_tag = header.find('a')
        if a_tag:
            if int(a_tag.text) >= 2000:
                year = int(a_tag.text)
                rows = soup.find_all('tr')
                for row in rows:
                    if row.find('a') == a_tag: 
                        win_tag = row.find('td', attrs = {'data-stat': 'W'})
                        wins = int(win_tag.text)
                        loss_tag = row.find('td', attrs = {'data-stat': 'L'})
                        losses = int(loss_tag.text)
                        conn, cur = connect_database()
                        create_mlb_tables(cur, conn, teams[team_abb])
                        insert_mlb_data(year, wins, losses, cur, conn, teams[team_abb])
                        conn.close()


                

                




    



