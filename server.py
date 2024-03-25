import inspect
import json
import random
from datetime import datetime

import questions_generator
import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
members = inspect.getmembers(questions_generator)

# Filter functions from members
questions_list = [member[1] for member in members if inspect.isfunction(member[1])]


def open_db_config():
    path = "db_conf.txt"
    try:
        with open(path, 'r') as f:
            text = f.read()
        config = json.loads(text)
        return config
    except OSError:
        print("file not existed or valid")
        exit(-1)


mysql_config = open_db_config()

try:
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
except Exception:
    print("could not connect to the mysql server")
    exit(-1)


@app.route('/api/all_countries', methods=['GET'])
def get_countries():
    query = """SELECT c.ID, c.country, c.flag
FROM mydb.countries AS c
LEFT JOIN (
    SELECT country, COUNT(*) AS country_count FROM (
        (SELECT a.country AS country FROM mydb.historical_event AS a) 
        UNION ALL
        (SELECT birth_country AS country FROM mydb.figure) 
        UNION ALL
        (SELECT death_country AS country FROM mydb.figure) 
        UNION ALL
        (SELECT idparticipantscol AS country FROM mydb.war_participants)
    ) AS combined_table_alias
    GROUP BY country
) cc ON c.ID = cc.country
ORDER BY IFNULL(cc.country_count, 0) DESC;
"""
    cursor.execute(query)
    result = cursor.fetchall()
    return jsonify(result)


### scoreboard - return the top users with the highest score
@app.route('/api/scoreboard', methods=['GET'])
def scoreboard():
    ### execute query from the db
    cursor.execute("""
    SELECT b.nickname, avg(a.score) as average FROM mydb.lesson as a, mydb.user as b
    where b.idUser = a.user
    group by a.user order by average desc
    LIMIT 10
    """)
    scoreboard = cursor.fetchall()
    return jsonify({'board': scoreboard})


### login
@app.route('/api/login/<nickname>/<password>', methods=['GET'])
def login(nickname, password):
    cursor.execute("SELECT iduser FROM user WHERE nickname='{}' and password = '{}'".format(nickname, password))
    result = cursor.fetchall()
    if len(result) != 0:
        return jsonify(result[0][0]), 200
    else:
        return jsonify({'message': 'no registered'}), 400


### register
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    nickname = data['nickname']
    email = data['email']
    password = data['password']
    cursor.execute(f"SELECT * FROM user WHERE email = '{email}' or nickname = '{nickname}'")
    result = cursor.fetchall()
    if len(result) != 0:
        return jsonify({'message': 'already registered'}), 400
    else:
        cursor.execute(f"INSERT into user (nickname, email, password) VALUES(%s, %s, %s)", (nickname, email,
                                                                                            password))
        user_id = cursor.lastrowid
        conn.commit()
        return jsonify({"user_id": user_id}), 200


### learn mode
@app.route('/api/learn', methods=['POST'])
def learn():
    data = request.json
    countries = data['countries']
    start_year = data['start_year']
    end_year = data['end_year']
    user = data['user']
    ### insert as lesson to the db
    query = """
    INSERT into lesson (user,start_time,end_time) VALUES (%s, %s, %s)
    """
    values = (user, start_year, end_year)
    cursor.execute(query, values)
    conn.commit()
    lesson_id = cursor.lastrowid
    for country in countries:
        query = """
            INSERT into lesson_country (idcountry,idlesson) VALUES (%s, %s)
            """
        values = (country, lesson_id)
        cursor.execute(query, values)
    conn.commit()
    ### extract the lesson events, figure and periods
    ### event query
    query = f"""
    SELECT Title, Year, Month, day, description
    FROM mydb.historical_event as a, mydb.lesson as b, mydb.lesson_country as c
    WHERE b.idlesson = {lesson_id}  and c.idlesson = {lesson_id} and a.year < b.end_time and a.year > b.start_time and 
    a.country = 
    c.idcountry ORDER BY rand() LIMIT 20"""
    cursor.execute(query)
    events = cursor.fetchall()
    clean_events = [{"Title": event[0], "date": str(event[3]) + "." + str(event[2]) + "." + str(event[1]), "description": event[4]} for
                    event in
                    events]
    ### periods
    query = f"""
    SELECT distinct Title, Description, start_time, end_time
    FROM (SELECT Historical_Period
    FROM mydb.historical_event as a, mydb.lesson as b, mydb.lesson_country as c
    WHERE b.idlesson = {lesson_id}  and c.idlesson = {lesson_id} and a.year < b.end_time and a.year > b.start_time and a.country = 
    c.idcountry) as d, mydb.historical_period
    WHERE d.Historical_Period = historical_period.ID ORDER BY rand() LIMIT 20
    """
    cursor.execute(query)
    wars_periods = cursor.fetchall()
    periods = [{"Title": per[0], "description": per[1], "start time": per[2], "end time": per[3]} for per in
               wars_periods]
    ### figures
    query = f"""
    (SELECT distinct Name, photo, description 
    FROM mydb.figure as a, mydb.lesson as b, mydb.lesson_country as c
    WHERE ((a.year_birth <= b.start_time and a.year_death >= b.start_time ) or (a.year_death <= b.end_time and a.year_birth >= b.start_time) or (a.year_birth >= b.start_time and a.year_birth <=b.end_time)) 
    and b.idlesson = c.idlesson and c.idlesson = {lesson_id} and (a.birth_country = c.idcountry or a.death_country = c.idcountry))
    UNION
    (SELECT distinct Name, photo, description 
    FROM mydb.figure as a, mydb.event_figures as b, (SELECT ID
    FROM mydb.historical_event as a, mydb.lesson as b, mydb.lesson_country as c
    WHERE b.idlesson = {lesson_id}  and c.idlesson = {lesson_id} and a.year < b.end_time and a.year > b.start_time and 
    a.country = c.idcountry) as c
    WHERE c.ID = b.idevent and a.ID = idfigure) ORDER BY rand()  LIMIT 20
    """
    cursor.execute(query)
    figures = cursor.fetchall()
    figures_clean = [{"Name":fig[0],"description":fig[1],"picture":fig[2]} for fig in figures]
    return jsonify({'lesson': lesson_id, 'wars and periods': periods, 'events': clean_events, 'figures': figures_clean})


### test mode
@app.route('/api/test', methods=['GET'])
def test():
    data = request.args
    lesson_id = data['lesson_id']
    questions = []
    counter = 8
    while counter > 0:
        rand_func = random.choice(questions_list)
        question = rand_func(lesson_id,cursor)
        if question['question'] in [quiz['question'] for quiz in questions]:
            continue
        if len(question['options']) == 4:
            counter -= 1
            questions.append(question)

    return jsonify({'questions': questions})


### submit test
@app.route('/api/submit_test', methods=['POST'])
def submit_test():
    data = request.json
    lesson_id = data['lesson_id']
    score = data['score']
    test_time = datetime.now()
    query = "UPDATE lesson SET score=%s, testing_time=%s WHERE idlesson=%s"
    values = (score, test_time, lesson_id)
    cursor.execute(query, values)
    conn.commit()
    return jsonify({}), 200


##get recomended countries
@app.route('/api/recomended_countries', methods=['GET'])
def get_recomended_countries():
    data = request.args
    user_id = data['user_id']
    query = f"""SELECT  c.country
FROM (SELECT ID, country from mydb.countries where continent = 
(SELECT a.continent from (SELECT continent,COUNT(*) AS count  FROM mydb.lesson,mydb.lesson_country,mydb.countries
WHERE user = {user_id} and lesson.idlesson = lesson_country.idlesson and lesson_country.idcountry = countries.ID
group by continent LIMIT 1) AS a)) AS c
LEFT JOIN (
    SELECT country, COUNT(*) AS country_count FROM (
        (SELECT a.country AS country FROM mydb.historical_event AS a) 
        UNION ALL
        (SELECT birth_country AS country FROM mydb.figure) 
        UNION ALL
        (SELECT death_country AS country FROM mydb.figure) 
        UNION ALL
        (SELECT idparticipantscol AS country FROM mydb.war_participants)
    ) AS combined_table_alias
    GROUP BY country
) cc ON c.ID = cc.country
ORDER BY IFNULL(cc.country_count, 0) DESC LIMIT 10
"""
    cursor.execute(query)
    result = cursor.fetchall()
    return jsonify(result)



if __name__ == '__main__':
    app.run(debug=True)
