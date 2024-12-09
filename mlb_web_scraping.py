import json
import os
import sqlite3
from bs4 import BeautifulSoup
import requests

#Create the MLB Databases
DATABASE_NAME = 'final_crime_time_database.db'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
def connect_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    return conn, cur

def create_mlb_tables(cur, conn, team):
    '''
    Creates a table for storing MLB regular season data with unique constraints to avoid duplication.
    '''

    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS {team} (
            season INTEGER,
            wins INTEGER,
            losses INTEGER,
            key INTEGER,
            UNIQUE(season)  -- Ensures season-year data is unique
        )
    ''')
    conn.commit()


def gather_team_data(team_abb):
    '''
    Gathers data for a given team from Baseball Reference.
    
    Returns:
        A list of dictionaries containing season, wins, and losses data.
    '''
    url = f'https://www.baseball-reference.com/teams/{team_abb}/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    print(f"Fetching data for {team_abb}: Status {r.status_code}")
    
    table = soup.find('tbody')
    rows = table.find_all('tr') if table else []
    
    data = []
    for row in rows:
        year_cell = row.find('th', {'data-stat': 'year_ID'})
        win_cell = row.find('td', {'data-stat': 'W'})
        loss_cell = row.find('td', {'data-stat': 'L'})

        if year_cell and win_cell and loss_cell:
            year_tag = year_cell.find('a')
            if year_tag and int(year_tag.text) >= 2000:  # Only process years >= 2000
                year = int(year_tag.text)
                wins = int(win_cell.text)
                losses = int(loss_cell.text)
                data.append({'season': year, 'wins': wins, 'losses': losses})
    
    return data

def insert_data_into_db(data, team, cur, conn, max_records=25):
    '''
    Inserts data into the database, ensuring no duplicates and up to max_records are added.
    '''
    new_record_count = 0
    for record in data:
        if new_record_count >= max_records:
            print(f"Reached the limit of {max_records} new records for {team}. Stopping insertions.")
            break
        
        cur.execute(f'''
            SELECT 1 FROM {team} WHERE season = ?
        ''', (record['season'],))
        
        if cur.fetchone() is None:  # Record does not exist
            cur.execute(f'''
                INSERT INTO {team} (season, wins, losses, key) VALUES (?, ?, ?, ?)
            ''', (record['season'], record['wins'], record['losses'], 1))
            conn.commit()
            new_record_count += 1
            print(f"Inserted: Season={record['season']}, Wins={record['wins']}, Losses={record['losses']} into {team}")
        else:
            print(f"Record for Season={record['season']} already exists in {team}, skipping.")
            return False
    print(f"Inserted {new_record_count} new records for {team}.")
    return True

# Define teams
teams = {
    'DET': 'Detroit_Tigers',
    'TEX': 'Texas_Rangers',
    'BOS': 'Boston_Red_Sox',
    'LAD': 'Los_Angeles_Dodgers',
    'PHI': 'Philadelphia_Phillies'
}

conn, cur = connect_database()

for team_abb in teams:
    create_mlb_tables(cur, conn, teams[team_abb])

    

# Main script logic
for team_abb, team_name in teams.items():
    print(f"\nProcessing team: {team_name} ({team_abb})")
    
     
    
    # Gather data for the team
    team_data = gather_team_data(team_abb)
    if insert_data_into_db(team_data, team_name, cur, conn):
        print(f"Gathered {len(team_data)} records for {team_name}.")
        
        # Insert data into the database
        insert_data_into_db(team_data, team_name, cur, conn)
        
        conn.close()
        print(f"Finished processing {team_name}.")
        break  # Only process one team per run

                

                




    



