import json
from flask import Flask, request, Response
from infastructure_files.support import *

# creating web framework functionality
app = Flask(__name__)

# routes go here
@app.route("/")
def index():
    return Response(json.dumps("home page"), status=200, mimetype="application/json")

@app.route("/ping")
def ping():
    return Response(json.dumps("PONG"), status=200, mimetype="application/json")

@app.route("/register", methods=["POST"])
def register():
    """ Add the user to the user table."""
    email = "test@okay.com"
    first_name = "test"
    last_name = "TEST"
    password = "testPassword"

    try:
        # create a connection to the database
        connection, cursor = connect_to_database()
        # use the cursor to send user info to db
        cursor.callproc("i_user", email, first_name, last_name, password)
        results = unpack_results(stored_results=cursor.stored_results())
        print(results)
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
    return Response(json.dumps(f"user {email} inserted"), status=200, mimetype="application/json")

    

@app.route("/users", methods=["GET"])
def users():
    """ bring back the user table. """
    try:
        # create a connection to the database
        connection, cursor = connect_to_database()
        # use the cursor to call the get the user table
        cursor.callproc("s_usertable")
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
