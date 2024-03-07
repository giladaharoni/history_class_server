import random


def which_one_participant_in_the_event(lesson_id, cursor):
    ## select relevant event, pick one as random
    query = f"""
        SELECT ID, Title
        FROM mydb.historical_event as a, mydb.lesson as b, mydb.lesson_country as c, mydb.event_figures as d
        WHERE b.idlesson = {lesson_id}  and c.idlesson = {lesson_id} and a.year < b.end_time and a.year > b.start_time and 
        a.country = c.idcountry and d.idevent=a.ID
        ORDER BY RAND () LIMIT 1"""
    cursor.execute(query)
    event = cursor.fetchall()
    ### pick someone who participate in it
    query = f"""
    SELECT Name
    FROM mydb.event_figures as a, mydb.figure as b
    WHERE a.idevent = {event[0][0]} and a.idfigure = b.ID
    ORDER BY RAND () LIMIT 1
    """
    cursor.execute(query)
    figure = cursor.fetchall()
    ### pick three who doesn't but from the same countries and years
    query = f"""
    SELECT Name
    FROM mydb.figure as a,mydb.lesson as b, mydb.lesson_country as c
    WHERE a.ID not in (SELECT idfigure FROM mydb.event_figures WHERE idevent = {event[0][0]}) and b.idlesson = 
    c.idlesson and b.idlesson = {lesson_id} and (((a.year_birth <= b.start_time and a.year_death >= b.start_time ) or (a.year_death <= b.end_time and a.year_birth >= b.start_time) or (a.year_birth >= b.start_time and a.year_birth <=b.end_time))
     and (a.birth_country = c.idcountry or a.death_country = c.idcountry))
     ORDER BY RAND () LIMIT 3
    """
    cursor.execute(query)
    event_title = event[0][1]
    question = f"Who take part in {event_title}?"
    wrong_answers = [i[0] for i in cursor.fetchall()]
    answers = wrong_answers+figure
    random.shuffle(answers)
    right_answer = figure[0]
    return {"question": question, "options": answers, "right_answer": right_answer}


def which_occor_in_the_year(lesson_id, cursor):
    ## select relevant event, pick one as random
    query = f"""
            SELECT ID, Title, year
            FROM mydb.historical_event as a, mydb.lesson as b, mydb.lesson_country as c, mydb.event_figures as d
            WHERE b.idlesson = {lesson_id}  and c.idlesson = {lesson_id} and a.year < b.end_time and a.year > b.start_time and 
            a.country = c.idcountry and d.idevent=a.ID
            ORDER BY RAND () LIMIT 1"""
    cursor.execute(query)
    event = cursor.fetchall()
    ### pick three other events from the same time and country of the lesson
    query = f"""
        SELECT Title
        FROM mydb.historical_event as a,mydb.lesson as b, mydb.lesson_country as c
        WHERE a.ID != {event[0][0]} and b.idlesson = 
        c.idlesson and b.idlesson = {lesson_id} and a.Year between b.start_time and b.end_time
         ORDER BY RAND () LIMIT 3
        """
    cursor.execute(query)
    event_year = event[0][2]
    question = f"which event happend in {event_year}?"
    answers = cursor.fetchall() + [event[0][1]]
    random.shuffle(answers)
    right_answer = event
    return {"question": question, "options": answers, "right_answer": right_answer}

def who_died_in(lesson_id, cursor):
    ## select a random figure
    query = f"""
    SELECT Name, year_death
    FROM mydb.figure as a,mydb.lesson as b, mydb.lesson_country as c
    WHERE b.idlesson = 
    c.idlesson and b.idlesson = {lesson_id} and (((a.year_birth <= b.start_time and a.year_death >= b.start_time ) or (a.year_death <= b.end_time and a.year_birth >= b.start_time) or (a.year_birth >= b.start_time and a.year_birth <=b.end_time))
     and (a.birth_country = c.idcountry or a.death_country = c.idcountry)) and a.year_death is not null
     ORDER BY RAND () LIMIT 1
"""

    cursor.execute(query)
    figure = cursor.fetchall()
    figure_death = figure[0][1]
    figure_name = figure[0][0]

    ### pick three who doesn't but from the same countries and years
    query = f"""
SELECT name
        FROM mydb.figure as a,mydb.lesson as b, mydb.lesson_country as c
        WHERE a.ID not in (SELECT idfigure FROM mydb.event_figures WHERE year_death = {figure_death}) and b.idlesson = 
        c.idlesson and b.idlesson = {lesson_id} and (((a.year_birth <= b.start_time and a.year_death >= b.start_time ) or (a.year_death <= b.end_time and a.year_birth >= b.start_time) or (a.year_birth >= b.start_time and a.year_birth <=b.end_time))
         and (a.birth_country = c.idcountry or a.death_country = c.idcountry))
         ORDER BY RAND () LIMIT 3
        """
    cursor.execute(query)
    question = f"Who died in {figure_death}?"
    answers = cursor.fetchall() + [figure_name]
    random.shuffle(answers)
    right_answer = [figure_name]
    return {"question": question, "options": answers, "right_answer": right_answer}


def who_born_in(lesson_id, cursor):
    ## select a random figure
    query = f"""
        SELECT Name, year_birth
        FROM mydb.figure as a,mydb.lesson as b, mydb.lesson_country as c
        WHERE a.ID not in (SELECT idfigure FROM mydb.event_figures WHERE year_death = 1930) and b.idlesson = 
        c.idlesson and b.idlesson = {lesson_id} and (((a.year_birth <= b.start_time and a.year_death >= b.start_time ) or (a.year_death <= b.end_time and a.year_birth >= b.start_time) or (a.year_birth >= b.start_time and a.year_birth <=b.end_time))
         and (a.birth_country = c.idcountry or a.death_country = c.idcountry))
         ORDER BY RAND () LIMIT 1
    """

    cursor.execute(query)
    figure = cursor.fetchall()
    figure_birth = figure[0][1]
    figure_name = figure[0][0]

    ### pick three who doesn't but from the same countries and years
    query = f"""
    SELECT name
            FROM mydb.figure as a,mydb.lesson as b, mydb.lesson_country as c
            WHERE a.ID not in (SELECT idfigure FROM mydb.event_figures WHERE year_birth = {figure_birth}) and b.idlesson = 
            c.idlesson and b.idlesson = {lesson_id} and (((a.year_birth <= b.start_time and a.year_death >= b.start_time ) or (a.year_death <= b.end_time and a.year_birth >= b.start_time) or (a.year_birth >= b.start_time and a.year_birth <=b.end_time))
             and (a.birth_country = c.idcountry or a.death_country = c.idcountry))
             ORDER BY RAND () LIMIT 3
            """
    cursor.execute(query)
    question = f"Who born in {figure_birth}?"
    wrong_answers = [i[0] for i in cursor.fetchall()]
    answers = wrong_answers + [figure_name]
    random.shuffle(answers)
    right_answer = [figure_name]

    return {"question": question, "options": answers, "right_answer": right_answer}


# def figure_country_birth():
#     pass
#
#
# def figure_country_death():
#     pass
#
#
# def countries_in_wars():
#     pass
