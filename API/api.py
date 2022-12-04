import json
from flask import Flask, request, Response, render_template, redirect, session, url_for
from infastructure_files.support import *
from datetime import date

# creating web framework functionality
app = Flask(__name__)
app.secret_key = "hbvfhjbvhjbv!@#@$#$!DDFRG@#R@#V"

landing_page = "http://localhost:5000/"

# routes go here
@app.route('/home')
def home():
    if 'id' in session:
        return redirect(url_for('welcome'))
    return render_template("home.html")

@app.route('/about')
def about():
    return json.dumps("this is the about.")

@app.route('/logout')
def logout():
    if 'id' in session:
        session.pop('id', None)
    return render_template("home.html")

@app.route("/")
def index():
    if 'id' in session:
        return redirect(url_for('welcome'))
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
            session['id'] = id
            return redirect(landing_page + f"welcome")
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
                session['id'] = id
                return redirect(landing_page + f"welcome")
        except Exception as e:
            message = f"and error occurred: {e}"
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
            return Response(json.dumps(message), status=500, mimetype="application/json")
    return render_template('login.html', error=error)

@app.route("/welcome", methods=["GET"])
def welcome():
    if 'id' in session:
        id = session['id']
    else:
        id = 999999
    print(f"in the welcome route with the identifier {id}")
    return render_template('welcome.html', user_id = id)


@app.route('/create_survey', methods=["GET","POST"])
def create_survey():
    error = None
    if request.method == "POST":
        try:
            title = request.form['title']
            num_type1 = request.form['type1num']
            num_type2 =  request.form['type2num']
            start = request.form['start']
            end = request.form['end']
            desc = request.form['description']
        except Exception as e:
            print(f"the error is: {e}")
            return render_template('survey.html', error=e)
        print(f"title: {title}")
        print(f"num type 1: {num_type1}")
        print(f"num type 2: {num_type2}")
        print(f"description: {desc}")
        print(f"start: {start}")
        print(f"end: {end}")
        today = date.today()
        if 'id' in session:
            id = session['id']
        else:
            id = 999999
        try:
            # create a connection to the database
            connection, cursor = connect_to_database()
            # use the cursor register survey and get its id
            cursor.callproc("i_survey", (id, today, start, end, title, desc))
            result = unpack_results(stored_results=cursor.stored_results())
            print(result)
            connection.commit()
            cursor.close()
            connection.close()
            print("the connection is closed")
            survey_id = result.pop()
            sid = survey_id['in_surveyId']
            session['sid'] = sid
            return redirect(url_for('enter_question'))
        except Exception as e:
            message = f"and error occurred: {e}"
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
            return Response(json.dumps(message), status=500, mimetype="application/json")

    return render_template('survey.html', error=error)

@app.route("/enter_question", methods=["GET","POST"])
def enter_question():
    if 'sid' in session:
        sid = session['sid']
    else:
        sid = 999999
    questions = None
    error = None
    if request.method == "POST":
        try:
            if "type2" in request.form:
                print("it is a type 1")
                type = 2
            elif "type1" in request.form:
                print("it is a type 2")
                type = 1
            else:
                raise Exception("check a box")
            q = request.form["question"]
            print(f"type: {type}")
            print(f"question: {q}")
            try:
                # create a connection to the database
                connection, cursor = connect_to_database()
                # use the cursor register survey and get its id
                cursor.callproc("i_question", (sid, type, q, 0))
                result = unpack_results(stored_results=cursor.stored_results())
                print(result)
                connection.commit()
                cursor.close()
                connection.close()
                print("the connection is closed")
                return redirect(url_for('enter_question'))
            except Exception as e:
                message = f"and error occurred: {e}"
                if 'cursor' in locals():
                    cursor.close()
                if 'connection' in locals():
                    connection.close()
                return Response(json.dumps(message), status=500, mimetype="application/json")
        except Exception as e:
            error=f"error: {e}"
            return render_template('question.html', error=error, questions=questions)
    return render_template("question.html" ,error=error, questions=questions)


@app.route("/delete_survey", methods=["GET"])
def delete_survey():
    #deletes oldest survey
    """ delete a survey. """
    survey_id = 3

    try:
        # create a connection to the database
        connection, cursor = connect_to_database()
        # use the cursor to call the get the user table
        cursor.callproc("d_survey")
        confirm = unpack_results(stored_results=cursor.stored_results())
        print(confirm)
        connection.commit()
        cursor.close()
        connection.close()
        return Response(json.dumps(f"the survey was deleted"), status=200, mimetype="application/json")
    except Exception as error:
        message = f"and error occurred: {error}"
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
        return Response(json.dumps(message), status=200, mimetype="application/json")


    
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
    

    if 'id' in session:
        id = session['id']
    else:
        id = 999999
    print(f"in the welcome route with the identifier {id}")   
    error = None
    try:
        # create a connection to the database
        connection, cursor = connect_to_database()
        # use the cursor to call the get the user table
        cursor.callproc("s_usersurvey", (id,))
        results = unpack_results(stored_results=cursor.stored_results())
        #temp = results.pop()
        # surveys = list(temp.values())
        surveys = []
        # for v in temp.values():
        #     surveys.append(v)
        temp = results.pop()
        surveys.append(temp['title'])
        surveys.append(temp['id'])
        print(surveys)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as error:
        message = f"and error occurred: {error}"
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
        return render_template("survey_display.html", survey = surveys, error = error)
    return render_template("survey_display.html", survey = surveys ,error = error)
    #return Response(json.dumps(surveys), status=200, mimetype="application/json")
    


if __name__ == '__main__':
    app.run(debug=True)