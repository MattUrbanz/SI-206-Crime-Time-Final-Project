#visualizations.py

import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


DATABASE_NAME = 'crime_time_database.db'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
def connect_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    return conn, cur


def get_data_from_db(db_path, query):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the query to get the data
    cursor.execute(query)
    data = cursor.fetchall()
    
    # Close the connection
    conn.close()
    
    return data

# 2. Prepare Data for Linear Regression
def prepare_data(data):
    # Assuming the data is in the form of a list of tuples (x, y)
    x = np.array([row[0] for row in data]).reshape(-1, 1)  # X values (independent variable)
    y = np.array([row[1] for row in data])  # Y values (dependent variable)
    return x, y

# 3. Perform Linear Regression
def perform_linear_regression(x, y):
    # Create a linear regression model
    model = LinearRegression()
    
    # Fit the model to the data
    model.fit(x, y)
    
    # Get the slope (coefficient) and intercept
    slope = model.coef_[0]
    intercept = model.intercept_
    
    # Get predictions
    y_pred = model.predict(x)
    
    return slope, intercept, y_pred

# 4. Plot the Data and the Regression Line
def plot_data_and_regression_line(x, y, y_pred):
    plt.figure(figsize=(8, 6))
    
    # Scatter plot of the original data
    plt.scatter(x, y, color='blue', label='Data points')
    
    # Plot the regression line
    plt.plot(x, y_pred, color='red', label='Regression Line')
    
    # Add titles and labels
    plt.title('Linear Regression')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    
    # Show the plot
    plt.show()

# Main function
def main():
    # 1. Define the path to your SQLite database and the query to fetch the data
    db_path = 'your_database.db'  # Path to your SQLite database
    query = 'SELECT column_x, column_y FROM your_table;'  # SQL query to retrieve the data
    
    # 2. Fetch the data from the database
    data = get_data_from_db(db_path, query)
    
    # 3. Prepare the data for regression
    x, y = prepare_data(data)
    
    # 4. Perform linear regression
    slope, intercept, y_pred = perform_linear_regression(x, y)
    
    # Print the regression results
    print(f"Slope: {slope}")
    print(f"Intercept: {intercept}")
    
    # 5. Plot the data and the regression line
    plot_data_and_regression_line(x, y, y_pred)



