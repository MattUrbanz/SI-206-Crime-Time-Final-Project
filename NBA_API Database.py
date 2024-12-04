from nba_api.stats.endpoints import teamyearbyyearstats
from nba_api.stats.static import teams
import sqlite3

celtics_id = 1610612738
mavericks_id = 1610612742
clippers_id = 1610612746
lakers_id = 1610612747
sixers_id = 1610612755
pistons_id = 1610612765

id_list = [celtics_id, mavericks_id, clippers_id, lakers_id, sixers_id, pistons_id]

team_list = ["Celtics", "Mavericks", "Clippers", "Lakers", "76ers", "Pistons"]

def get_team_ids():
    all_teams = teams.get_teams()

    # Print team names and IDs
    for team in all_teams:
        print(f"ID: {team['id']}, Name: {team['full_name']}")

def get_team_data(id,startyear):
    '''
    Arguments
        id: team id
        startyear: Starting year of the season
    
    Returns
        data containing the team name, NBA season, wins, losses, and win percentage
    '''

    team_stats = teamyearbyyearstats.TeamYearByYearStats(team_id=id)
    df = team_stats.get_data_frames()[0]

    endyear = startyear + 1
    strendyear = str(endyear)
    season = str(startyear)+'-'+ strendyear[2] + strendyear[3]

    df = df[df['YEAR'] == season]

    return(df[['TEAM_NAME','YEAR', 'WINS', 'LOSSES', 'WIN_PCT']])

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
        cur.execute('DROP TABLE IF EXISTS ?', (team,))
        cur.execute('''
                    CREATE TABLE ? (season STRING, wins INTEGER, losses INTEGER)
                    ''')
    conn.commit()
    conn.close()

def insert_nba_data(season, win_amount, loss_amount, cur, conn, team):
    cur.execute('''
                INSERT INTO ? (season, wins, losses) VALUES ?, ?, ?
                ''', (team, season, win_amount, loss_amount))
    conn.commit()
    conn.close()

def make_nba_tables(cur, conn):
    '''
    Arguments
        cur: database cursor
        conn: database connection

    Returns
        None

    Notes
        Creates database for NBA teams including the Boston Celtics, Dallas Mavericks, Los Angeles Clippers, Los Angeles Lakers, 
        Philadelphia 76ers, and the Detroit Pistons. This database includes each teams win and loss counts for each season from 
        the 2000-01 season up until the NBA's most recently concluded season, 2023-24.
    '''

    #Making tables for teams
    create_nba_tables(cur,conn)

    #Putting team data into database
    for id in id_list:
        year = 2000
        while year <= 2023:
            df = get_team_data(id,year)
            insert_nba_data(df['YEAR'], df['WINS'], df['LOSSES'], cur, conn, df['TEAM_NAME'])
            year += 1