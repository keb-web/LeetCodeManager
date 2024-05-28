import sqlite3

# connect to database 'con' --> connection
con = sqlite3.connect("tutorial.db")
# initialiaze cursor. Used for fetching query results and executing statements
cur = con.cursor()

# # create table
# cur.execute("CREATE TABLE Questions(Name, Diffuculty, Date, Completed)")

# Selecting table
# NOTE: 'sqlite_master is a SQLite built-in table
# It is a "schema table" that is a database with descriptions of all other tables

# res = cur.execute("SELECT name FROM sqlite_master")
# print(res.fetchone())
# output: ('Questions',)

# Querying for nonExistent Table "Spam"
# res = cur.execute("SELECT name FROM sqlite_master WHERE name='spam'")
# print(res.fetchone() is None)


# Inserting data into the table
# cur.execute("""
#     INSERT INTO Questions (Name, Diffuculty, Date, Completed) VALUES
#         ('TWOSUM', 'EASY', '05/05/2024', True),
#         ('PRINT LEVEL ORDER BST', 'EASY', '05/06/2024', False),
#         ('KOKOBANANAS', 'EASY', '05/07/2024', False)
# """)
# NOTE: 'INSERT' statement implicitly opens a transaction
# Transactions need to be commited with "___.commit()" before changes are saved

# con.commit()

# Verifying correct insertion
# res = cur.execute("SELECT Name FROM Questions")
# print(res.fetchall())
# insert with cur.executemane(..)

# data = [
#     ("Balance BST", 'EASY', '05/08/2024', True),
#     ("LCA BST", 'EASY', '05/09/2024', False)
# ]
# cur.executemany("INSERT INTO Questions VALUES(?, ?, ?, ?)", data)
# con.commit()

# printing by row, attrib, and order
# for row in cur.execute("SELECT Date, Name FROM Questions ORDER by Date"):
#     print(row)

con.close()
