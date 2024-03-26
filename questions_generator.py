import random


def which_one_participant_in_the_event(lesson_id, cursor):
    ## select relevant event, pick one as random
    query = f"""
        SELECT ID, Title
        FROM db02.historical_event as a, db02.lesson as b, db02.lesson_country as c, db02.event_figures as d
        WHERE b.idlesson = {lesson_id}  and c.idlesson = {lesson_id} and a.year < b.end_time and a.year > b.start_time and 
        a.country = c.idcountry and d.idevent=a.ID
        ORDER BY RAND () LIMIT 1"""
    cursor.execute(query)
    event = cursor.fetchall()
    ### pick someone who participate in it
    query = f"""
    SELECT Name
    FROM db02.event_figures as a, db02.figure as b
    WHERE a.idevent = {event[0][0]} and a.idfigure = b.ID
    ORDER BY RAND () LIMIT 1
    """
    cursor.execute(query)
    figure = cursor.fetchall()
    ### pick three who doesn't but from the same countries and years
    query = f"""
    SELECT Name
    FROM db02.figure as a,db02.lesson as b, db02.lesson_country as c
    WHERE a.ID not in (SELECT idfigure FROM db02.event_figures WHERE idevent = {event[0][0]}) and b.idlesson = 
    c.idlesson and b.idlesson = {lesson_id} and (((a.year_birth <= b.start_time and a.year_death >= b.start_time ) or (a.year_death <= b.end_time and a.year_birth >= b.start_time) or (a.year_birth >= b.start_time and a.year_birth <=b.end_time))
     and (a.birth_country = c.idcountry or a.death_country = c.idcountry))
     ORDER BY RAND () LIMIT 3
    """
    cursor.execute(query)
    event_title = event[0][1]
    question = f"Who took part in {event_title}?"
    wrong_answers = [i[0] for i in cursor.fetchall()]
    answers = wrong_answers+list(figure[0])
    random.shuffle(answers)
    right_answer = figure[0][0]
    return {"question": question, "options": answers, "right_answer": right_answer}


def which_occor_in_the_year(lesson_id, cursor):
    ## select relevant event, pick one as random
    query = f"""
            SELECT ID, Title, year
            FROM db02.historical_event as a, db02.lesson as b, db02.lesson_country as c, db02.event_figures as d
            WHERE b.idlesson = {lesson_id}  and c.idlesson = {lesson_id} and a.year < b.end_time and a.year > b.start_time and 
            a.country = c.idcountry and d.idevent=a.ID
            ORDER BY RAND () LIMIT 1"""
    cursor.execute(query)
    event = cursor.fetchall()
    ### pick three other events from the same time and country of the lesson
    query = f"""
        SELECT Title
        FROM db02.historical_event as a,db02.lesson as b, db02.lesson_country as c
        WHERE a.ID != {event[0][0]} and b.idlesson = 
        c.idlesson and b.idlesson = {lesson_id} and a.Year between b.start_time and b.end_time
         ORDER BY RAND () LIMIT 3
        """
    cursor.execute(query)
    event_year = event[0][2]
    question = f"which event happend in {event_year}?"
    answers = [i[0] for i in cursor.fetchall()] + [event[0][1]]
    random.shuffle(answers)
    right_answer = event[0][1]
    return {"question": question, "options": answers, "right_answer": right_answer}

def who_died_in(lesson_id, cursor):
    ## select a random figure
    query = f"""
    SELECT Name, year_death
    FROM db02.figure as a,db02.lesson as b, db02.lesson_country as c
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
        FROM db02.figure as a,db02.lesson as b, db02.lesson_country as c
        WHERE a.ID not in (SELECT idfigure FROM db02.event_figures WHERE year_death = {figure_death}) and b.idlesson = 
        c.idlesson and b.idlesson = {lesson_id} and (((a.year_birth <= b.start_time and a.year_death >= b.start_time ) or (a.year_death <= b.end_time and a.year_birth >= b.start_time) or (a.year_birth >= b.start_time and a.year_birth <=b.end_time))
         and (a.birth_country = c.idcountry or a.death_country = c.idcountry))
         ORDER BY RAND () LIMIT 3
        """
    cursor.execute(query)
    question = f"Who died in {figure_death}?"
    answers = [ans[0] for ans in cursor.fetchall()] + [figure_name]
    random.shuffle(answers)
    right_answer = [figure_name]
    return {"question": question, "options": answers, "right_answer": right_answer[0]}


def who_born_in(lesson_id, cursor):
    ## select a random figure
    query = f"""
        SELECT Name, year_birth
        FROM db02.figure as a,db02.lesson as b, db02.lesson_country as c
        WHERE b.idlesson = 
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
            FROM db02.figure as a,db02.lesson as b, db02.lesson_country as c
            WHERE a.ID not in (SELECT idfigure FROM db02.event_figures WHERE year_birth = {figure_birth}) and b.idlesson = 
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

    return {"question": question, "options": answers, "right_answer": right_answer[0]}


def figure_occupation(lesson_id, cursor):
    query = f"""
    SELECT a.Name, a.ID, e.name
    FROM db02.figure as a,db02.lesson as b, db02.lesson_country as c, figure_occupation as d, occupation as e
    WHERE b.idlesson = c.idlesson and b.idlesson = {lesson_id} and (((a.year_birth <= b.start_time and a.year_death >= 
    b.start_time ) or (a.year_death <= b.end_time and a.year_birth >= b.start_time) or (a.year_birth >= b.start_time and a.year_birth <=b.end_time))
    and (a.birth_country = c.idcountry or a.death_country = c.idcountry)) and d.idfigure = a.ID and e.idoccupation = d.idoccupation
    order by rand() limit 1
    """
    cursor.execute(query)
    figure = cursor.fetchall()
    figure_id = figure[0][1]
    figure_name = figure[0][0]
    occupation = figure[0][2]
    options_query = f"""
    SELECT a.name
    FROM occupation as a
    WHERE a.idoccupation not in (SELECT idoccupation from figure_occupation where idfigure = {figure_id})
    order by rand() limit 3"""
    cursor.execute(options_query)
    options = cursor.fetchall()
    answers = [occ[0] for occ in options] + [occupation]
    random.shuffle(answers)
    question = "Which of those occupation was one of "+figure_name+"'s occupations?"
    return {"question": question, "options": answers, "right_answer": occupation}



def country_in_wars(lesson_id, cursor):
    query = f"""SELECT c.idwar, c.idcountry, e.Title, d.country FROM 
    (SELECT idwar, idcountry
    FROM war_participants as a,(SELECT idcountry FROM db02.lesson_country WHERE idlesson={lesson_id}) as b 
    WHERE b.idcountry = a.idparticipantscol) as c, countries as d, historical_period as e
    WHERE c.idcountry = d.ID and e.ID = c.idwar
    order by rand() limit 1"""
    cursor.execute(query)
    war_country_pair = cursor.fetchall()
    try:
        country_id = war_country_pair[0][1]
        country_name = war_country_pair[0][3]
        war_name = war_country_pair[0][2]
        sec_query = f"""
        SELECT Title
        FROM historical_period, war_participants
        WHERE historical_period.ID = war_participants.idwar and war_participants.idwar not in (SELECT idwar FROM 
        war_participants WHERE idparticipantscol={country_id})
        order by rand() limit 3"""
        cursor.execute(sec_query)
        another_wars = cursor.fetchall()
        question = "In which wars, did " + country_name + " take part of?"
        answers = [war[0] for war in another_wars] + [war_name]
        random.shuffle(answers)
        return {"question": question, "options": answers, "right_answer": war_name}
    except IndexError:
        return {"question": "question", "options": [], "right_answer": "2"}
