import json
from flask import Flask, request, Response
import mysql.connector

db_user = "root"
db_password = "password"
db_host = "localhost"
db_name = "databaseproject"

# creating web framework functionality
app = Flask(__name__)

def connect_to_database():
    connection = mysql.connector.connect(user=db_user, password=db_password,
                                         host=db_host, database=db_name)
    cursor = connection.cursor()
    return connection, cursor

def unpack_results(stored_results):
    results = []
    col_names = []
    for result in stored_results:
        # Get the column names from the first data entry
        if len(col_names) == 0:
            for desc in result.description:
                col_names.append(desc[0])
        for row in result.fetchall():
            formatted_row = {}
            for i in range(len(col_names)):
                formatted_row.update({col_names[i]: row[i]})
            results.append(formatted_row)
    return results

# routes go here
@app.route("/")
def index():
    return Response(json.dumps("home page"), status=200, mimetype="application/json")

@app.route("/ping")
def ping():
    return Response(json.dumps("PONG"), status=200, mimetype="application/json")

@app.route("/register")
def register():
    return Response(json.dumps("this is the future, believe it or not"), status=200, mimetype="application/json")

@app.route("/users", methods=["GET"])
def users():
    try:
        # create a connection to the database
        connection, cursor = connect_to_database()
        # use the cursor to call the get the user table
        cursor.callproc("g_usertable")
        users = unpack_results(stored_results=cursor.stored_results())
        print(users)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as error:
        message = f"and error occurred: {error}"
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
        return Response(json.dumps(message), status=200, mimetype="application/json")
    return Response(json.dumps("okay"), status=200, mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True)
