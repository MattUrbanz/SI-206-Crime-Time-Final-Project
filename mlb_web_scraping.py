import json
import os
import sqlite3
from bs4 import BeautifulSoup
import requests

#Create the MLB Databases
DATABASE_NAME = 'final_crime_time_database.db'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
def connect_database():
    '''
    Establishes a connection to the SQLite database and returns the connection and cursor objects.
Parameters:
None
What the code does:
- Connects to the SQLite database specified by the 'DATABASE _PATH variable.
- Creates a cursor object, which is used to execute SQL commands on the connected database.
- Returns both the connection object and the cursor object to be used for database operations.
Returns:
tuple: A tuple containing two objects:
-conn (sqlite3.Connection): The connection object used to manage the database connection and commit transactions.
- cur (sqlite3.Cursor): The cursor object used to execute SOL commands on the database.
    '''
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    return conn, cur

def create_mlb_tables(cur, conn, team):
    '''
    Creates a table in the database for storing MLB regular season data for a specific team.
Ensures that there are no duplicate entries for the same season using a UNIQUE constraint.
Parameters:
cur (salite3.Cursor): The cursor object used to execute SOL commands on the database. conn (sqlite3.Connection): The connection object used to commit changes to the database. team (str): The name of the team for which the table is being created. This will be used as the table's name.
What the code does:
- Executes an SOL command to create a new table if it does not already exist.
- The table will store the following columns: season (INTEGER), wins (INTEGER), losses (INTEGER), and key (INTEGER).
- The 'season column is constrained to be unique, ensuring no duplicate entries for a specific season.
Returns:
None: This function does not return any value. It modifies the database by creating the table.  
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
   Gathers data for a given MLB team from Baseball Reference, including season, wins, and losses.
Parameters:
team_abb (str): The abbreviation for the team (e.g., 'DET' for the Detroit Tigers, 'BOS' for the Boston Red Sox).
What the code does:
- Constructs a URL to access the team's page on Baseball Reference using the provided team abbreviation.
- Sends a GET request to fetch the content of the page.
- Uses BeautifulSoup to parse the HTML content of the page.
- Finds the table containing the regular season data and iterates over each row.
- For each row, it extracts the season year, number of wins, and losses.
- Only data for seasons 2000 and beyond is included.
- Each valid row is stored as a dictionary with 'season', 'wins', and 'losses' and added to a list.
Returns:
list: A list of dictionaries, where each dictionary contains the following keys:
'season' (int): The year of the MLB season.
'wins' (int): The number of wins the team had in that season.
'losses' (int): The number of losses the team had in that season.
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
    Inserts MLB team data into the corresponding database table, ensuring that no duplicate records are added and up to a specified maximum number of records are inserted.
Parameters:
data (list): A list of dictionaries containing the data to be inserted. Each dictionary should have the following keys:
'season' (int): The season year.
'wins' (int): The number of wins the team had in that season.
- 'losses' (int): The number of losses the team had in that season.
team (str): The name of the table where the data should be inserted (e.g., 'NYM', 'BOS"). cur (sqlite3.Cursor): The cursor object used to execute SQL queries on the database. conn (sqlite3.Connection): The connection object used to commit changes to the database.
max_records (int, optional): The maximum number of records to insert. Default is 25. The function will stop inserting if this number is reached.
What the code does:
- Iterates through the list of data records.
- For each record, it checks whether a record for the same season already exists in the corresponding table.
- If the record does not exist, it inserts the new data (season, wins, losses, and a key value of 1).
- If the record already exists, it skips inserting that record.
- Limits the insertion to the specified number of records ('max_records").
- Commits the data to the database after each successful insertion.
Returns:
bool: Returns 'True if records were inserted successfully. If no records were inserted (due to reaching the max limit or duplicates), returns 'False.
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

                

                




    



