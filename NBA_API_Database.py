from nba_api.stats.endpoints import teamyearbyyearstats
from nba_api.stats.static import teams
import sqlite3
import os

celtics_id = 1610612738
mavericks_id = 1610612742
clippers_id = 1610612746
lakers_id = 1610612747
sixers_id = 1610612755
pistons_id = 1610612765

DATABASE_NAME = "crime_time_database.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

id_list = [celtics_id, mavericks_id, clippers_id, lakers_id, sixers_id, pistons_id]
team_list = ["Celtics", "Mavericks", "Clippers", "Sixers", "Lakers", "Pistons"]

def connect_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    return [cur, conn]

def get_team_data(id,startyear):
    '''
    Arguments
        id: team id
        startyear: Starting year of the season
    
    Returns
        string of data containing the team name (string), NBA season (string), wins (int), and losses (int)
    '''

    team_stats = teamyearbyyearstats.TeamYearByYearStats(team_id=id)
    df = team_stats.get_data_frames()[0]

    endyear = startyear + 1
    strendyear = str(endyear)
    season = str(startyear)+'-'+ strendyear[2] + strendyear[3]

    df = df[df['YEAR'] == season]

    team_name = df['TEAM_NAME'].values[0]
    season = df['YEAR'].values[0]
    wins = df['WINS'].values[0]
    losses = df['LOSSES'].values[0]

    return [team_name, season, wins, losses]

def create_nba_tables(cur, conn):
    '''
    Arguments
        cur: database cursor
        conn: database connection
    
    Returns
        none

    Notes
        Creates tables for storing NBA regular season data
    '''

    for team in team_list:
        cur.execute(f'''
                    CREATE TABLE IF NOT EXISTS {team}
                    (season STRING, wins INTEGER NOT NULL, losses INTEGER NOT NULL)
                    ''')
    conn.commit()

def insert_nba_data(cur, conn):
    '''
    Arguments
        cur: database cursor
        conn: database connection
    
    Returns
        none

    Notes
        Adds data for relevant NBA teams into their respective databases
    '''

    index = -1
    for id in id_list:
        index += 1
        for year in range(2000, 2023):
            data = get_team_data(id, year)
            team = team_list[index]
    
            cur.execute(f'''
                INSERT INTO {team} (season, wins, losses) VALUES (?, ?, ?)
                ''', (data[1], data[2], data[3]))
    conn.commit()

cnc = connect_database()
create_nba_tables(cnc[0], cnc[1])
insert_nba_data(cnc[0], cnc[1])