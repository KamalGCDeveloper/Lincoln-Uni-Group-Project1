from flask import logging, render_template, session
from app import app
from app.db import get_db_connection
from app.helper_query_competitions import fetch_competition_by_competition_id, fetch_public_current_competitions, fetch_public_future_competitions, fetch_public_past_competitions

@app.route('/competitions')
def competitions():
    current_competitions = fetch_public_current_competitions()
    past_competitions = fetch_public_past_competitions()
    future_competitions = fetch_public_future_competitions()
    return render_template('competitions.html', current_competitions=current_competitions, past_competitions=past_competitions, future_competitions=future_competitions)

@app.route('/competitions/details/<int:competition_id>')
def competition_details(competition_id):
    # Use helper methods in query_competitions to fetch competitions
    competition = fetch_competition_by_competition_id(competition_id)
    user_role = session.get('role', None)
    user_id = session.get('user_id')
    
    # Get competitor name if user have voted
    competitor_id = None
    competitor_name = None
    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT competitor_id FROM votes WHERE user_id = %s AND competition_id = %s',
            (user_id, competition_id)
        )
        user_voted = cursor.fetchone()

        if user_voted:
            competitor_id = user_voted[0]
            cursor.execute(
                'SELECT competitor_name FROM competitors WHERE competitor_id = %s',
                (competitor_id,)
            )
            competitor_name = cursor.fetchone()[0]
        cursor.close()
        conn.close()

    return render_template('competition_details.html', user_role = user_role, competition=competition,voted_competitor_name=competitor_name, user_voted=competitor_id)


    