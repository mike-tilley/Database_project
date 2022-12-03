import json
from flask import Flask, request, Response, render_template, redirect
from infastructure_files.support import *
from datetime import date

# creating web framework functionality
app = Flask(__name__)

landing_page = "http://localhost:5000/"

# routes go here
@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return json.dumps("this is the about.")


@app.route("/")
def index():
    # return json.dumps("home page")
    # return Response(json.dumps("home page"), status=200, mimetype="application/json")
    return render_template("home.html")

@app.route("/ping")
def ping():
    return Response(json.dumps("PONG"), status=200, mimetype="application/json")
    

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

@app.route("/register", methods=["GET", "POST"])
def register():
    """ register a user. first a users email is checked to make sure it is not in use currently.
        Then a user is registered and there id is returned to use in further routing. """

    error = None
    if request.method == "POST":
        email = request.form['email']
        password =  request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        print(f"email: {email}")
        print(f"password: {password}")
        print(f"first: {email}")
        print(f"last: {password}")
        try:
            # create a connection to the database
            connection, cursor = connect_to_database()
            # use the cursor check if the email is already in use
            cursor.callproc("s_user", (email,))
            results = unpack_results(stored_results=cursor.stored_results())
            if len(results) != 0:
                error = 'email already in use'
                return render_template('register.html', error=error)
            
            #email not in use so register the user
            cursor.callproc("i_user", ( email, first_name, last_name, password))
            result = unpack_results(stored_results=cursor.stored_results())
            print(result)
            connection.commit()
            cursor.close()
            connection.close()
            print("the connection is closed")
            user_id = result.pop()
            id = user_id['id']
            return redirect(landing_page + f"welcome/{id}")
        except Exception as e:
            message = f"and error occurred: {e}"
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
            return Response(json.dumps(message), status=500, mimetype="application/json")
    return render_template('register.html', error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    """ log a user in. """
    error = None
    if request.method == "POST":
        email = request.form['email']
        password =  request.form['password']
        print(f"email: {email}")
        print(f"password: {password}")
        try:
            # create a connection to the database
            connection, cursor = connect_to_database()
            # use the cursor to call the get the user table
            cursor.callproc("s_login",(email,password))
            result = unpack_results(stored_results=cursor.stored_results())
            connection.commit()
            cursor.close()
            connection.close()
            print("the connection is closed")
            if len(result) == 0:
                error = 'invalid username or password'
                return render_template('login.html', error=error)
            else:
                user_id = result.pop()
                id = user_id['id']
                return redirect(landing_page + f"welcome/{id}")
        except Exception as e:
            message = f"and error occurred: {e}"
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
            return Response(json.dumps(message), status=500, mimetype="application/json")
    return render_template('login.html', error=error)

@app.route("/welcome/<identifier>", methods=["GET"])
def welcome(identifier):
    print(f"in the welcome route with the identifier {identifier}")
    return render_template('welcome.html', user_id=identifier)

# @app.route("/login", methods=["GET"])
# def login():
#     """ log a user in. """
#     email = "test3@okay.com"
#     password = "test3Password"

#     try:
#         # create a connection to the database
#         connection, cursor = connect_to_database()
#         # use the cursor to call the get the user table
#         cursor.callproc("s_login",(email,password))
#         user_id = unpack_results(stored_results=cursor.stored_results())
#         print(user_id)
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return Response(json.dumps(f"the user id is : {user_id}"), status=200, mimetype="application/json")
#     except Exception as error:
#         message = f"and error occurred: {error}"
#         if 'cursor' in locals():
#             cursor.close()
#         if 'connection' in locals():
#             connection.close()
#         return Response(json.dumps(message), status=500, mimetype="application/json")


# @app.route("/delete_user", methods=["GET"])
# def delete_user():
#     """ delete a user. """
#     user_id = 3

#     try:
#         # create a connection to the database
#         connection, cursor = connect_to_database()
#         # use the cursor to call the get the user table
#         cursor.callproc("d_user",(user_id,))
#         confirm = unpack_results(stored_results=cursor.stored_results())
#         print(confirm)
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return Response(json.dumps(f"the user was deleted"), status=200, mimetype="application/json")
#     except Exception as error:
#         message = f"and error occurred: {error}"
#         if 'cursor' in locals():
#             cursor.close()
#         if 'connection' in locals():
#             connection.close()
#         return Response(json.dumps(message), status=200, mimetype="application/json")

# @app.route("/make_survey", methods=["GET"])
# def make_survey():
#     """ bring back the user table. """
#     # survery table stuff
#     user_id = 2
#     start = date(2022, 12, 1)
#     end = date(2022, 12, 25)
#     participants = 1
#     description = "test survey for insertion mapping"

#     # questionaire stuff

#     q1 = "how old are you"
#     a1 = "1000"
#     q2 = "where do you live"
#     a2 = "Florida"
#     q3 = "how much do you like this project"
#     a3 = "5"
   
#     try:
#         # create a connection to the database
#         connection, cursor = connect_to_database()
#         # use the cursor to call the get the user table
#         cursor.callproc("i_survey",(user_id, start, end, participants, description, q1, a1, q2, a2, q3, a3))
#         confirm = unpack_results(stored_results=cursor.stored_results())
#         print(confirm)
#         connection.commit()
#         cursor.close()
#         connection.close()
#     except Exception as error:
#         message = f"and error occurred: {error}"
#         if 'cursor' in locals():
#             cursor.close()
#         if 'connection' in locals():
#             connection.close()
#         return Response(json.dumps(message), status=200, mimetype="application/json")
#     return Response(json.dumps(f"The user id: {user_id} had a survey created."), status=200, mimetype="application/json")

@app.route('/view_active_available', methods=['GET'])
def view_active_available():
    """ this route will take a user id in the request paramters and find all the surverys available for the user to take based on
        the surveys start, end, and status or whether or not that have taken the survey once. """
    print("this is the place holder")
    return json.dumps("viewing all the active surveys right now.")

@app.route('/view_survey_results', methods=['GET'])
def view_survey_results():
    """ this route will need to take a users id in the request parameters and find all the users surveys that have been
        comepleted and bring back the answers in some organized way. """
    print("this is the place holder")
    return json.dumps("this will bring back all the survey results.")


if __name__ == '__main__':
    app.run(debug=True)
