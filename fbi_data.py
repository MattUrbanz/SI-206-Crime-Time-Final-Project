import requests
import json
import sqlite3
import os


API_BASE_URL = 'https://api.usa.gov/crime/fbi/cde/hate-crime/state/'
API_KEY = '1MriSHUQ3jGzF9vvb3pLRqqSinNoZ6jIElx984Ee'  
DATABASE_NAME = "final_crime_time_database.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

#connecting to sqlite database 
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

#creating tables
def create_state_tables(state_abbrs, cur, conn):
    '''
    Creates tables for storing hate crime counts for each state in the database.
Each table is named according to the state abbreviation followed by ' hate crime counts'.
Parameters:
state_abbrs (list): A list of state abbreviations (e.g., ['CA', 'NY', 'TX']) for which tables should be created. cur (sqlite3.Cursor): The cursor object used to execute SQL queries on the database. conn (sqlite. Connection): The connection object used to commit changes to the database.
What the code does:
- Iterates through each state abbreviation in the 'state abbrs list.
- For each state, it creates a table named
'stateabbrv_hate_crime_counts (e.g., 'CA_hate_crime _counts').
- The table has two columns:
'year' (INTEGER): Represents the year of the hate crime data.
'hate_crime_count' (INTEGER): Represents the number of hate crimes reported in that year.
- The CREATE TABLE IF NOT EXISTS SOL statement ensures that the table is only created if it does not already exist.
Returns:
None: This function does not return any value. It modifies the database by creating tables.'''
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
    '''
    Fetches the hate crime count for a given state and year using an API.
Parameters:
state (str): The abbreviation of the state for which the hate crime data is being requested (e.g., 'CA', 'NY').
year (int): The year for which the hate crime data is being requested (e.g., 2022).
What the code does:
- Constructs an API request to retrieve hate crime data for the given state and year.
- The params dictionary includes the date range ('from and 'to'), type of data ('all'), and the API key required for authentication.
- The headers dictionary specifies the expected response format as JSON.
- The function sends the request to the API and retrieves the data (not fully implemented here).
Returns:
dict: The function will likely return a dictionary containing the hate crime data, but this depends on the remaining code (which is not provided here).
Notes:
You should ensure that the API KEY variable is defined elsewhere in the code and contains a valid API key.
    '''
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
    '''
    Populates the state tables with hate crime data for each state and year within the specified range.
The function will insert up to a total of 25 records across all state tables in one run.
Parameters:
state_abbrs (list): A list of state abbreviations (e.g., ['CA', 'NY', 'TX' J) for which hate crime data should be inserted. start_year (int): The start year of the range of years for which the data should be fetched and inserted. end year (int): The end year of the range of years for which the data should be fetched and inserted. cur (sqlite3.Cursor): The cursor object used to execute SQL queries on the database. conn (sqlite3.Connection): The connection object used to commit changes to the database.
What the code does:
- Loops through the list of state abbreviations and for each state, it populates the hate crime data table for the years between start year' and end _year' (inclusive).
- For each year in the specified range, it checks if the data for that state and year already exists in the corresponding table («state _abbr›_hate _crime_counts")
- If data for the year does not exist, it calls the get _hate _crime_count function to retrieve the hate crime count.
- If the data is valid (i.e., the count is not 'None'), it inserts the data into the table.
- The function stops once 25 records have been inserted across all tables in a single run (i.e., once the global record limit is reached).
Returns:
None: The function does not return any value. It modifies the database by inserting data into state tables.
    '''
    max_records_per_run = 25  # Limit across all tables
    total_record_count = 0  # Counter for all insertions in this run

    for state in state_abbrs:
        table_name = f"{state}_hate_crime_counts"

        for year in range(start_year, end_year + 1):
            if total_record_count >= max_records_per_run:
                print("Reached the 25-record limit for this run across all tables.")
                conn.commit()
                return  # Stop once the global limit is reached

            # Check if the record already exists for the given year
            cur.execute(f'''
                SELECT 1 FROM {table_name} WHERE year = ?
            ''', (year,))
            if cur.fetchone():
                print(f"Data for {state} in {year} already exists. Skipping...")
                continue  # Skip existing records

            # Fetch hate crime count for the year
            count = get_hate_crime_count(state, year)
            if count is not None:  # Ensure we have valid data
                cur.execute(f'''
                    INSERT INTO {table_name} (year, hate_crime_count)
                    VALUES (?, ?)
                ''', (year, count))
                total_record_count += 1  # Increment the global counter
                print(f"Inserted data into {table_name}: {year}, {count}")

            if total_record_count >= max_records_per_run:
                print("Reached the 25-record limit for this run across all tables.")
                conn.commit()
                return  # Stop once the global limit is reached

    conn.commit()  # Commit any remaining changes
    print("Data population completed without exceeding the limit.")






def main():
    '''
    Main function that orchestrates the entire process of setting up the database, creating tables, populating tables with data, and closing the database connection.
What the code does:
- Establishes a connection to the database and retrieves the connection and cursor objects.
- Defines a list of state abbreviations ( STATE_ABBRV) for which data will be processed.
- Calls the create_state_tables function to create tables for each state in the 'STATE _ABBRV list.
- Defines a range of years (from start _year to end_year") and calls the populate_state_tables function to insert hate crime data for each state and year within the specified range.
- Closes the database connection after the operations are complete.
- Prints a success message to indicate the completion of database operations.
Returns:
None: This function does not return any value. It runs the entire workflow for database setup and population.
'''
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