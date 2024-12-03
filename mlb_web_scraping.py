import json
import os
import sqlite3
from bs4 import BeautifulSoup
import requests

#Create the MLB Databases
def create_mlb_tables(cur,conn):
    '''
    Arguments
        cur: databse cursor 
        conn: database connection
    Returns
        None
    Notes:
        Creates table for storing MLB regular season data
    '''
    for team in teams:
        cur.execute('DROP TABLE IF EXISTS ?', (team,))
        cur.execute('''
            CREATE TABLE ? (season INTEGER, wins INTEGER, losses INTEGER)
                    ''', (team,))
    conn.commit()
    conn.close()

def insert_mlb_data(season, win_amount, loss_amount, cur, conn, team):
    '''
    Arguments
        cur: databse cursor 
        conn: database connection
        season: Integer
        win_amount: Integer
        loss_amoun: Integer

    Returns
        None
    Notes:
        Inserts record for each regular season past 2000 into database
    '''
    cur.execute('''
        INSERT INTO ? (season, wins, losses) VALUES ?, ?, ?
                ''', (team, season, win_amount, loss_amount))
    conn.commit()
    conn.close()


teams = {'DET' : 'Detroit-Tigers', 'TEX' : 'Texas-Rangers', 'BOS' : 'Boston-Red-Sox', 'LAD' : 'Los-Angeles-Dodgers', 'PHI' : 'Philladelphia-Phillies'}
r = requests.get('https://www.baseball-reference.com/teams/DET')
soup = BeautifulSoup(r.content, 'html.parser')
team_abbs = teams.keys()

for team_abb in team_abbs:
    url = 'https://www.baseball-reference.com/teams/' + team_abb + '/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    print(r.status_code)
    table = soup.find('tbody')
    
    
    table_headers = soup.find_all('th', attrs = {'data-stat': 'year_ID', 'class': 'left'})
    print(teams[team_abb])

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
                        print('Year: ', year, ' Wins: ', wins, ' Losses: ', losses)
                        #insert_mlb_data(year, wins, losses, cur, conn)
                

                




    



