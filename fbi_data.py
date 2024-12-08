import requests
import json
import sqlite3
import os


API_BASE_URL = 'https://api.usa.gov/crime/fbi/cde/hate-crime/state/'
API_KEY = '1MriSHUQ3jGzF9vvb3pLRqqSinNoZ6jIElx984Ee'  
DATABASE_NAME = "crime_time_database.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

#connecting to sqlite database 
def connect_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    return conn, cur

#creating tables
def create_state_tables(state_abbrs, cur, conn):
    for state in state_abbrs:
        table_name = f"{state}_hate_crime_counts"  # e.g., 'CA_hate_crime_counts'
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                year INTEGER NOT NULL,
                hate_crime_count INTEGER NOT NULL
            )
        ''')
        print(f"Table '{table_name}' created or already exists.")
    conn.commit()

def get_hate_crime_count(state, year):
    params = {
        'from': f'01-{year}',
        'to': f'12-{year}',
        'type': 'all',
        'API_KEY': API_KEY
    }
    headers = {
        'accept': 'application/json'
    }

    url = f"{API_BASE_URL}{state}"


    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'bias_section' in data:
            return sum(data['bias_section']['offense_type'].values())
        else:
            print(f"No bias_section in data for {year}.")
            return 0
    else:
        print(f"Failed to fetch data for {state} in {year}: {response.status_code}, {response.content}")
        return 0
    
# put data into tables 
def populate_state_tables(state_abbrs, start_year, end_year, cur, conn):
    record_count = 0  # Counter to track the number of records inserted

    for state in state_abbrs:
        if record_count >= 25:
            break  # Stop if we've already inserted 25 records

        table_name = f"{state}_hate_crime_counts"
        for year in range(start_year, end_year + 1):
            if record_count >= 25:
                break  # Stop if we've already inserted 25 records
            
            count = get_hate_crime_count(state, year)
            cur.execute(f'''
                INSERT INTO {table_name} (year, hate_crime_count)
                VALUES (?, ?)
            ''', (year, count))
            record_count += 1  # Increment the record counter

            print(f"Inserted data into {table_name}: {year}, {count}")
            
            if record_count >= 25:
                print("Reached the 25-record limit for this run.")
                break  # Exit if the limit is reached

        conn.commit()



        
def main():
    # Database setup
    conn, cur = connect_database()
    STATE_ABBRV = ['CA', 'MI', 'TX', 'PA', 'MA']
    
    # Create tables
    create_state_tables(STATE_ABBRV, cur, conn)
    
    # Populate tables with data
    start_year = 2000
    end_year = 2023
    populate_state_tables(STATE_ABBRV, start_year, end_year, cur, conn)

    # Close database connection
    conn.close()
    print("Database operations completed successfully.")

if __name__ == "__main__":
    main()