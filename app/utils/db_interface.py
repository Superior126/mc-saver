import os
import sqlite3
import json

class DatabaseInterface:
    def __init__(self):
        self.db = None

        # Check if db dir exists
        if os.path.exists('/var/lib/mc_saver'):
            db_dir = '/var/lib/mc_saver'
        else:
            os.makedirs('/var/lib/mc_saver')
            db_dir = '/var/lib/mc_saver'

        # Connect to db
        self.db = sqlite3.connect(db_dir + '/data.db')
        self.cursor = self.db.cursor()

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
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table['name']} ({table_schema})")
            self.db.commit()

        # Ensure all columns are present
        for table in self.db_template:
            for column in table['columns']:
                self.cursor.execute(f"PRAGMA table_info({table['name']})")
                columns = self.cursor.fetchall()

                column_names = [column[1] for column in columns]

                if column['name'] not in column_names:
                    column_schema = f"{column['name']} {column['type']}"

                    # Check if column is primary key
                    if "primary_key" in column and column['primary_key']:
                        column_schema += ' PRIMARY KEY'

                    # Add column to table
                    self.cursor.execute(f"ALTER TABLE {table['name']} ADD COLUMN {column_schema}")
                    self.db.commit()
