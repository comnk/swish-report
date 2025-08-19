from api.core.db import get_db_connection

# Now connect to that database
cnx = get_db_connection()
cursor = cnx.cursor()

cursor.execute("DROP DATABASE IF EXISTS swish_report")
print("Database swish_report dropped.")
cnx.close()