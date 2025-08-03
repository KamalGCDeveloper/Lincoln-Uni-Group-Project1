import mysql.connector
from connect import dbuser, dbpass, dbhost, dbport, dbname

# Connect to MySQL database
def get_db_connection():
    conn = mysql.connector.connect(
        user=dbuser, password=dbpass, host=dbhost, port=dbport, database=dbname
    )
    return conn