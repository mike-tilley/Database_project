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
    if 'sid' in session:
        session.pop('sid', None)
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
            # result = cursor.fetchall()
            print(result)
            user_id = result.pop()
            id = user_id['id']
            session['id'] = id
            connection.commit()
            cursor.close()
            connection.close()
            print("the connection is closed")
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
            emails= request.form['emails']
            start = request.form['start']
            end = request.form['end']
            desc = request.form['description']
        except Exception as e:
            print(f"the error is: {e}")
            return render_template('survey.html', error=e)
        print(f"title: {title}")
        print(f"emails: {emails}")
        print(f"description: {desc}")
        print(f"start: {start}")
        print(f"end: {end}")
        today = date.today()
        email_list = emails.split(" ")
        print(email_list)
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
            survey_id = result.pop()
            sid = survey_id['in_surveyId']
            session['sid'] = sid

            # if any user is a valid user relate them as a participant
            for email in email_list:
                cursor.callproc("s_user", (email,))
                results = unpack_results(stored_results=cursor.stored_results())
                if len(results) != 0:
                    temp = results.pop()
                    temp_id = temp['id'] 
                    cursor.callproc("i_participant", (temp_id, sid))
                    results = unpack_results(stored_results=cursor.stored_results())
                else:
                    print("the user email was not found")
            # close the connection 
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



@app.route('/view_active_available', methods=['GET', 'POST'])
def view_active_available():
    """ this route will take a user id in the request paramters and find all the surverys available for the user to take based on
        the surveys start, end, and status or whether or not that have taken the survey once. """

    error = None
    surveys = None
    if 'id' in session:
        id = session['id']
    else:
        id = 999999
    today = date.today()
    print(f"id: {id} and today is {today}")
    try:
        # create a connection to the database
        print("in try of view active")
        connection, cursor = connect_to_database()
        # use the cursor register survey and get its id
        cursor.callproc("s_participate", (id, today))
        result = unpack_results(stored_results=cursor.stored_results())
        print(result)
        surveys = result
        connection.commit()
        cursor.close()
        connection.close()
        print("the connection is closed")
    except Exception as e:
        message = f"and error occurred: {e}"
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
        return Response(json.dumps(message), status=500, mimetype="application/json")

    if request.method == "POST":
        print("nothing posting yet")
        print(f"the result is: {result}")
        try:
            sid = int(request.form['sid'])
            print(f"the sid is: {sid}")
            survey_ids = []
            for available_surveys in result:
                for k, v in available_surveys.items():
                    if k == 'id':
                        survey_ids.append(v)
            print(survey_ids)
            if sid not in survey_ids:
                print("raising exception")
                raise Exception("no matching survey id")
        except Exception as e:
            error = e
            return render_template('survey_display.html', surveys=surveys, error=error)
        session['sid'] = sid
        print("redirecting")

        # redirecting to take the survey with user id and survey id stored in the session
        return redirect(url_for('take_survey'))
    
    return render_template('survey_display.html', surveys=surveys, error=error)


@app.route("/take_survey", methods=["GET","POST"])
def take_survey():
    """ this will take a survey id and bring back all the questions associated to that survey. 
        Then the answers will be recorded in the answer table. """

    questions = None
    error = None

    if 'id' in session:
        id = session['id']
    else:
        id = 999999
    if 'sid' in session:
        sid = session['sid']
    else:
        id = 999999
    try:
        # create a connection to the database
        connection, cursor = connect_to_database()
        # use the cursor register survey and get its id
        cursor.callproc("s_questions", (sid,))
        result = unpack_results(stored_results=cursor.stored_results())
        print(result)
        questions = result
        connection.commit()
        cursor.close()
        connection.close()
        print("the connection is closed")
    except Exception as e:
        message = f"and error occurred: {e}"
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
        return Response(json.dumps(message), status=500, mimetype="application/json")
    if request.method == "POST":
        """ unpack the input and call the stored procedure 'i_answer' to post the answers to answer table, 
            then post to the user_answers relation."""
        raw_input = request.form['a']
        answer_list = raw_input.split(",")
        print(answer_list)
        q_a_dict = {}
        question_id_list = []
        for entry in result:
            for k, v in entry.items():
                if k == 'id':
                    question_id_list.append(v)
        print(f"qid list: {question_id_list}")
        for i in range(len(question_id_list)):
            q_a_dict.update({question_id_list[i]: answer_list[i]})
        try:
            # create a connection to the database
            connection, cursor = connect_to_database()
            # use the cursor loop and insert answers
            for qid, a in q_a_dict.items():
                print(f"about to insert {id} {qid} {a}")
                cursor.callproc("i_answer", (id, qid, a))
                result = unpack_results(stored_results=cursor.stored_results())
                print(result)
            connection.commit()
            cursor.close()
            connection.close()
            print("the connection is closed")
            redirect(url_for('welcome'))
        except Exception as e:
            message = f"and error occurred: {e}"
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
            return Response(json.dumps(message), status=500, mimetype="application/json")
    

    return render_template('q_and_a.html', questions=questions, error=error)
    
    # questions = None
    # error = None
    # if request.method == "POST":
    #     try:
    #         if "type2" in request.form:
    #             print("it is a type 1")
    #             type = 2
    #         elif "type1" in request.form:
    #             print("it is a type 2")
    #             type = 1
    #         else:
    #             raise Exception("check a box")
    #         q = request.form["question"]
    #         print(f"type: {type}")
    #         print(f"question: {q}")
    #         try:
    #             # create a connection to the database
    #             connection, cursor = connect_to_database()
    #             # use the cursor register survey and get its id
    #             cursor.callproc("i_question", (sid, type, q, 0))
    #             result = unpack_results(stored_results=cursor.stored_results())
    #             print(result)
    #             connection.commit()
    #             cursor.close()
    #             connection.close()
    #             print("the connection is closed")
    #             return redirect(url_for('enter_question'))
    #         except Exception as e:
    #             message = f"and error occurred: {e}"
    #             if 'cursor' in locals():
    #                 cursor.close()
    #             if 'connection' in locals():
    #                 connection.close()
    #             return Response(json.dumps(message), status=500, mimetype="application/json")
    #     except Exception as e:
    #         error=f"error: {e}"
    #         return render_template('question.html', error=error, questions=questions)
    # return render_template("question.html" ,error=error, questions=questions)


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


@app.route("/survey_results", methods=["GET"])
def survey_results():
    try:
        sid = session["sid"]
        connection, cursor = connect_to_database()
        cursor.callproc("s_survey_title", (sid,))
        results = unpack_results(stored_results=cursor.stored_results())
        for result in results:
            title = result["title"]
        print(title)

        cursor.callproc("s_survey_description", (sid,))
        results = unpack_results(stored_results =cursor.stored_results())
        for result in results:
            description = result["description"]
        print(description)

        cursor.callproc("s_start_date", (sid,))
        results = unpack_results(stored_results =cursor.stored_results())
        for result in results:
            start = result["start"]
        print(start)


        cursor.callproc("s_end_date", (sid,))
        results = unpack_results(stored_results =cursor.stored_results())
        for result in results:
            end = result["end"]
        print(end)


        questions = []
        cursor.callproc("s_survey_questions", (sid,))
        print(sid)
        # results = unpack_results(stored_results =cursor.stored_results())
        # print(results)
        # for result in results:
        #     questions.append( result["q"])
        for result in cursor.stored_results():
            questions = result.fetchall()
        print(questions)

        

        connection.commit()
        cursor.close()
        connection.close()
        return render_template('user_survey_results.html', title = title, description = description, start = start, end = end, questions = questions)
    except Exception as error:
        message = f"and error occurred: {error}"
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
        return Response(json.dumps(message), status=200, mimetype="application/json")

# @app.route('/view_survey_results', methods=['GET'])
# def view_survey_results():
#     """ this route will need to take a users id in the request parameters and find all the users surveys that have been
#         comepleted and bring back the answers in some organized way. """
#     print("this is the place holder")
#     return json.dumps("this will bring back all the survey results.")


@app.route('/view_survey_results', methods=['GET', 'POST'])
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
        for result in cursor.stored_results():
            data = result.fetchall()
        
        #results = unpack_results(stored_results=cursor.stored_results())
        print(data)
        #temp = results.pop()
        # surveys = list(temp.values())
        # for v in temp.values():
        #     surveys.append(v)

        connection.commit()
        cursor.close()
        connection.close()
    except Exception as error:
        message = f"and error occurred: {error}"
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
        return render_template("user_survey_display.html", survey = data, error = error)

    if request.method == "POST":
        print("the button is being clicked")
        sid = request.form['sid']
        session['sid'] = sid
        return redirect(url_for(f'survey_results'))
    return render_template("user_survey_display.html", survey = data ,error = error)
    #return Response(json.dumps(surveys), status=200, mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True)
