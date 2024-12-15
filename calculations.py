import sqlite3
import matplotlib.pyplot as plt
import json

calculations = {}

def write_data_to_json(filename, data):
    '''
    Writes the given data to a JSON file with the specified filename.
Parameters:
filename (str): The name of the file where the data will be written. This file will be created or overwritten. data (dict or list): The data to be written to the JSON file. This can be a dictionary, list, or any JSON-serializable object.
What the code does:
- Opens the specified file in write mode ('w') with UTF-8 encoding. If the file does not exist, it will be created.
- Uses ison.dump() to serialize the data and write it to the file. The data will be formatted with an indentation of 4 spaces for readability.
- Prints a success message indicating that the data has been successfully written to the specified file.
Returns:
None
    '''
    with open(filename, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    print(f"Data successfully written to {filename}")



# Connect to the database
conn = sqlite3.connect('final_crime_time_database.db')
cur = conn.cursor()

# 1. Calculate state_average_crime_count and create a bar graph
# Query to calculate average crime count for each state
query_avg_crime = """
SELECT
    'MA' AS state, AVG(hate_crime_count) AS average_crime
FROM MA_hate_crime_counts
UNION
SELECT
    'MI', AVG(hate_crime_count)
FROM MI_hate_crime_counts
UNION
SELECT
    'PA', AVG(hate_crime_count)
FROM PA_hate_crime_counts
UNION
SELECT
    'TX', AVG(hate_crime_count)
FROM TX_hate_crime_counts
UNION
SELECT
    'CA', AVG(hate_crime_count)
FROM ca_hate_crime_counts;
"""
cur.execute(query_avg_crime)
results_avg_crime = cur.fetchall()

# Process data for the bar graph
states = [row[0] for row in results_avg_crime]
avg_crimes = [row[1] for row in results_avg_crime]

calculations['average_crime_counts_by_state'] = [
    {"State": row[0], "Average Crime Count": row[1]} for row in results_avg_crime
]

# Create bar graph
plt.figure(figsize=(10, 6))
plt.bar(states, avg_crimes, color='skyblue', edgecolor='black')
plt.title('Average Hate Crime Counts by State (2000-2023)', fontsize=16)
plt.xlabel('State', fontsize=14)
plt.ylabel('Average Hate Crime Count', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 2. Calculate Year_MI_crime_loss_ratio and create a line graph
# Query to calculate the ratio of hate crime counts to Detroit Tigers losses by year
query_crime_loss_ratio = """
SELECT
    MI_hate_crime_counts.year,
    CAST(MI_hate_crime_counts.hate_crime_count AS FLOAT) /
    NULLIF(Detroit_Tigers.losses, 0) AS crime_loss_ratio
FROM
    MI_hate_crime_counts
JOIN
    Detroit_Tigers
ON
    MI_hate_crime_counts.year = Detroit_Tigers.season;
"""
cur.execute(query_crime_loss_ratio)
results_crime_loss_ratio = cur.fetchall()

# Process data for the line graph
years = [row[0] for row in results_crime_loss_ratio]
ratios = [row[1] for row in results_crime_loss_ratio]

calculations['mi_crime_loss_ratios'] = [
    {"Year": row[0], "Crime to Loss Ratio": row[1]} for row in results_crime_loss_ratio
]

# Create line graph
plt.figure(figsize=(12, 7))
plt.plot(years, ratios, marker='o', color='red', label='MI Crime/Loss Ratio')
plt.title('Michigan Hate Crime to Detroit Tigers Loss Ratio (2000-2023)', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Crime to Loss Ratio', fontsize=14)
plt.xticks(years, rotation=45, fontsize=12)
plt.yticks(fontsize=12)
plt.grid(alpha=0.5)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()


# 3. Calculate state_nfl_win_percentage and create a bar graph
# Query to calculate the win percentage for each state (MI, TX, MA, PA, CA)
query_nfl_win_percentage = """
SELECT
    'MI' AS state, 
    SUM(Lions.wins) * 1.0 / SUM(Lions.wins + Lions.losses) AS nfl_win_percentage
FROM Lions
UNION
SELECT
    'TX', 
    SUM(Cowboys.wins) * 1.0 / SUM(Cowboys.wins + Cowboys.losses)
FROM Cowboys
UNION
SELECT
    'MA', 
    SUM(Patriots.wins) * 1.0 / SUM(Patriots.wins + Patriots.losses)
FROM Patriots
UNION
SELECT
    'PA', 
    SUM(Eagles.wins) * 1.0 / SUM(Eagles.wins + Eagles.losses)
FROM Eagles
UNION
SELECT
    'CA', 
    SUM(Chargers.wins) * 1.0 / SUM(Chargers.wins + Chargers.losses)
FROM Chargers;
"""
cur.execute(query_nfl_win_percentage)
results_nfl_win_percentage = cur.fetchall()

# Process data for the bar graph
states = [row[0] for row in results_nfl_win_percentage]
win_percentages = [row[1] for row in results_nfl_win_percentage]
calculations['nfl_win_percentages_by_state'] = [
    {"State": row[0], "Win Percentage": row[1]} for row in results_nfl_win_percentage
]

# Create bar graph
plt.figure(figsize=(10, 6))
plt.bar(states, win_percentages, color='lightgreen', edgecolor='black')
plt.title('NFL Win Percentages by State (2000-2024)', fontsize=16)
plt.xlabel('State', fontsize=14)
plt.ylabel('NFL Win Percentage', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.ylim(0, 1)  # Since percentages range from 0 to 1
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()


query_cowboys_win_percentage_per_year = """
SELECT season, 
       SUM(wins) * 1.0 / (SUM(wins) + SUM(losses)) AS cowboys_win_percentage
FROM Cowboys
WHERE season BETWEEN 2000 AND 2023
GROUP BY season;
"""
cur.execute(query_cowboys_win_percentage_per_year)
cowboys_win_percentage_per_year = cur.fetchall()

# Fetch Crime Data for Texas (TX) from 2000-2023
query_tx_crime_data = """
SELECT year, hate_crime_count
FROM TX_hate_crime_counts
WHERE year BETWEEN 2000 AND 2022;
"""
cur.execute(query_tx_crime_data)
tx_crime_data = cur.fetchall()
scatter_data = list(zip([row[1] for row in tx_crime_data], win_percentages))
calculations['tx_crime_vs_cowboys_win'] = [
    {"Crime Count": crime, "Cowboys Win Percentage": win} 
    for crime, win in scatter_data
]

# Process the data: Create lists of win percentages and crime counts for each year
years = [row[0] for row in tx_crime_data]
crime_counts = [row[1] for row in tx_crime_data]

# Now, for each year in the crime data, we need to get the corresponding Cowboys' win percentage
win_percentages = []
for year in years:
    # Find the Cowboys' win percentage for the corresponding year
    for row in cowboys_win_percentage_per_year:
        if row[0] == year:
            win_percentages.append(row[1])
            break
#print(len(win_percentages))
#print(len(crime_counts))

# 4. Create a graph where each dot represents a different year
plt.figure(figsize=(10, 6))
plt.scatter(crime_counts, win_percentages, color='blue', label='Data Points', alpha=0.6)
plt.title('TX Crime Count vs. Cowboys Win Percentage (2000-2023)', fontsize=16)
plt.xlabel('Crime Count in Texas', fontsize=14)
plt.ylabel('Cowboys Win Percentage', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()


write_data_to_json('all_calculations.json', calculations)

# Close the database connection
conn.close()