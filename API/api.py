import json
from flask import Flask, request, Response
from infastructure_files.support import *
from datetime import date

# creating web framework functionality
app = Flask(__name__)

# routes go here
@app.route("/")
def index():
    # return json.dumps("home page")
    return Response(json.dumps("home page"), status=200, mimetype="application/json")

@app.route("/ping")
def ping():
    return Response(json.dumps("PONG"), status=200, mimetype="application/json")

@app.route("/register", methods=["GET"])
def register():
    """ Add the user to the user table."""
    email = "test@okay.com"
    first_name = "test2name"
    last_name = "TESTlastname"
    password = "testPassword"

    try:
        # create a connection to the database
        connection, cursor = connect_to_database()
        # use the cursor to send user info to db
        cursor.callproc("i_user", ( email, first_name, last_name, password))
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
    return Response(json.dumps(users), status=200, mimetype="application/json")


@app.route("/delete_user", methods=["GET"])
def delete_user():
    """ delete a user. """
    user_id = 3

    try:
        # create a connection to the database
        connection, cursor = connect_to_database()
        # use the cursor to call the get the user table
        cursor.callproc("d_user",(user_id,))
        confirm = unpack_results(stored_results=cursor.stored_results())
        print(confirm)
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

@app.route("/make_survey", methods=["GET"])
def make_survey():
    """ bring back the user table. """
    # survery table stuff
    user_id = 2
    start = date(2022, 12, 1)
    end = date(2022, 12, 25)
    participants = 1
    description = "test survey for insertion mapping"

    # questionaire stuff

    q1 = "how old are you"
    a1 = "1000"
    q2 = "where do you live"
    a2 = "Florida"
    q3 = "how much do you like this project"
    a3 = "5"
   
    try:
        # create a connection to the database
        connection, cursor = connect_to_database()
        # use the cursor to call the get the user table
        cursor.callproc("i_survey",(user_id, start, end, participants, description, q1, a1, q2, a2, q3, a3))
        confirm = unpack_results(stored_results=cursor.stored_results())
        print(confirm)
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
    return Response(json.dumps(f"The user id: {user_id} had a survey created."), status=200, mimetype="application/json")


if __name__ == '__main__':
    app.run(debug=True)
