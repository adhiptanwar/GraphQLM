import psycopg2
import psycopg2.extras


class Database:
    def __init__(self, database, user, password, host, port):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            # print("~~~~~~~ Connected to database successfully ~~~~~~~ ")
        except psycopg2.Error as e:
            print("Unable to connect to the database:", e)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            # print("~~~~~~~ Connection closed ~~~~~~~\n")

    def execute_query(self, query, var1, var2):
        if not self.connection:
            print("Not connected to the database.")
            return None
        try:
            cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(query, (var1, var2))
            records = cursor.fetchall()
            cursor.close()
            return records
        except psycopg2.Error as e:
            print("Error executing query:", e)
            return None

    # Add more methods for different database operations
    def get_1hop_triple_object(self, object, relation):
        query = "select * from kg_triples where object = %s and predicate = %s;"
        return self.execute_query(query, object, relation)

    def get_1hop_triple_subject(self, subject, relation):
        query = "select * from kg_triples where subject = %s and predicate = %s;"
        return self.execute_query(query, subject, relation)
