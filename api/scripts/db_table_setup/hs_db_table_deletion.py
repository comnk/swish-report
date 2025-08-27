from core.db import get_db_connection

# Now connect to that database
cnx = get_db_connection()
cursor = cnx.cursor()

