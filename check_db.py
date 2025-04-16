import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')  # Ensure the path is correct
cursor = conn.cursor()

# Execute a query to check users
cursor.execute("SELECT * FROM user")
users = cursor.fetchall()

# Print the users
for user in users:
    print(user)

# Close the connection
conn.close()
