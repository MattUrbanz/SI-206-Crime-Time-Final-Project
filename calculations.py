import sqlite3
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect('crime_time_database.db')
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


# 1. Calculate state_nfl_win_percentage and create a bar graph
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

# Close the database connection
conn.close()