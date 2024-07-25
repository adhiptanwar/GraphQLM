import sqlite3
import pandas as pd

class Database:
    def __init__(self, db_path, txt_file):
        self.db_path = db_path
        self.txt_file = txt_file
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            print("Connected to database successfully")
            self.create_table_from_txt()
        except sqlite3.Error as e:
            print("Unable to connect to the database:", e)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Connection closed")

    def create_table_from_txt(self):
        # Load the text file into a pandas DataFrame
        df = pd.read_csv(self.txt_file, delimiter='|', header=None, names=['subject', 'predicate', 'object'])
        # Write the DataFrame to the SQLite database
        df.to_sql('kg_triples', self.connection, if_exists='replace', index=False)
       

    def execute_query(self, query, params):
        if not self.connection:
            print("Not connected to the database.")
            return None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            records = cursor.fetchall()
            cursor.close()
            return records
        except sqlite3.Error as e:
            print("Error executing query:", e)
            return None

    def get_1hop_triple_object(self, object, relation):
        query = "SELECT * FROM kg_triples WHERE LOWER(object) = LOWER(?) AND predicate = ?;"
        return self.execute_query(query, (object, relation))

    def get_1hop_triple_subject(self, subject, relation):
        query = "SELECT * FROM kg_triples WHERE LOWER(subject) = LOWER(?) AND predicate = ?;"
        return self.execute_query(query, (subject, relation))
