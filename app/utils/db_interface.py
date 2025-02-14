import os
import sqlite3
import json
import uuid
import hashlib
import datetime

class DatabaseInterface:
    def __init__(self):
        pass

    def get_connection(self):
        # Check if db dir exists
        if os.path.exists('/var/lib/mc_saver'):
            db_dir = '/var/lib/mc_saver'
        else:
            os.makedirs('/var/lib/mc_saver')
            db_dir = '/var/lib/mc_saver'

        # Connect to db
        db = sqlite3.connect(db_dir + '/data.db')
        cursor = db.cursor()

        # Get current run directory
        run_dir = os.path.dirname(os.path.realpath(__file__))

        # Load database template
        with open(run_dir + '/../resources/database_template.json', 'r') as f:
            self.db_template = json.loads(f.read())
            f.close()

        # Ensure all tables are present
        for table in self.db_template:
            # Create table schema
            table_schema = ''

            for column in table['columns']:
                column_schema = f"{column['name']} {column['type']}"

                # Check if column is primary key
                if "primary_key" in column and column['primary_key']:
                    column_schema += ' PRIMARY KEY'

                # Add column to table schema
                table_schema += column_schema + ', '

            # Remove trailing comma and space
            table_schema = table_schema[:-2]

            # Create table
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table['name']} ({table_schema})")
            db.commit()

        # Ensure all columns are present
        for table in self.db_template:
            for column in table['columns']:
                cursor.execute(f"PRAGMA table_info({table['name']})")
                columns = cursor.fetchall()

                column_names = [column[1] for column in columns]

                if column['name'] not in column_names:
                    column_schema = f"{column['name']} {column['type']}"

                    # Check if column is primary key
                    if "primary_key" in column and column['primary_key']:
                        column_schema += ' PRIMARY KEY'

                    # Add column to table
                    cursor.execute(f"ALTER TABLE {table['name']} ADD COLUMN {column_schema}")
                    db.commit()

        return db

    def ensure_root_user_exist(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if root user exists
        root_user = cursor.execute("SELECT * FROM users WHERE rootUser = 1").fetchone()

        if not root_user:
            # Generate root user id
            root_user_id = str(uuid.uuid4())

            # Generate root user salt
            root_user_salt = os.urandom(16).hex()

            # Hash root user password
            root_user_password = hashlib.sha512(('root' + root_user_salt).encode()).hexdigest()

            # Insert root user into database
            cursor.execute("INSERT INTO users (userId, username, password, passwordSalt, rootUser) VALUES (?, ?, ?, ?, ?)", 
                                (root_user_id, 'root', root_user_password, root_user_salt, 1))
            conn.commit()

        conn.close()

    def login(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get user from database
        user = cursor.execute("SELECT userId, username, password, passwordSalt FROM users WHERE username = ?", 
                                   (username,)).fetchone()

        if not user:
            raise self.Exceptions.InvalidCredentials

        # Hash password
        password_hash = hashlib.sha512((password + user[3]).encode()).hexdigest()

        # Check if password is correct
        if password_hash != user[2]:
            raise self.Exceptions.InvalidCredentials
        
        # Generate a session token
        session_token = str(uuid.uuid4())

        # Get current UTC time and calculate expiration time
        current_time = datetime.datetime.now(datetime.timezone.utc)
        expiration_time = current_time + datetime.timedelta(days=1)
        expiration_time_str = expiration_time.strftime('%Y-%m-%d %H:%M:%S')

        # Add session to database
        cursor.execute("INSERT INTO sessions (sessionId, userId, expiration) VALUES (?, ?, ?)", 
                            (session_token, user[0], expiration_time_str))
        conn.commit()
        conn.close()

        return session_token, expiration_time_str
    
    def logout(self, session_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sessions WHERE sessionId = ?", (session_id,))
        conn.commit()
        conn.close()
    
    class Exceptions:
        class InvalidCredentials(Exception):
            """Raised when invalid credentials are provided"""
            pass
            