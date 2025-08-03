from datetime import datetime
import os
from flask import flash, jsonify, redirect, render_template, request, session, url_for
from app import app
from app.db import get_db_connection
from app.helper_query_competitions import fetch_competition_by_competition_id, fetch_competition_start_date, fetch_competitions_for_select, fetch_public_current_competitions, fetch_public_future_competitions, fetch_public_past_competitions, fetch_public_unfinalised_competitions
from app.helper_query_votes import fetch_daily_votes, fetch_suspicious_competitions, fetch_votes_by_ip, fetch_votes_for_competition, vote_status_check
@app.route('/scrutineer_dashboard', methods=['GET', 'POST'])
def scrutineer_dashboard():

    return render_template('scrutineer_dashboard.html')

@app.route('/daily_votes_check', methods=['GET', 'POST'])
def daily_votes_check():
    today_date = datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        competition_id = request.form.get('competition_id')
        date = request.form.get('date')
        daily_votes = fetch_daily_votes(competition_id, date)
        competitions = fetch_public_current_competitions()
        min_date = fetch_competition_start_date(competition_id)
        return render_template('daily_votes_check.html', daily_votes=daily_votes, competition_id=competition_id, selected_date=date, competitions=competitions, min_date=min_date)
        
    competitions = fetch_public_current_competitions()
    return render_template('daily_votes_check.html', competitions=competitions, today_date=today_date)
    
@app.route('/ip_address_check', methods=['GET', 'POST'])
def ip_address_check():
    competitions_for_select = fetch_competitions_for_select()
    if request.method == 'POST':
        competition_id = request.form.get('competition_id')
        votes = fetch_votes_for_competition(competition_id) if competition_id else []
        return render_template('ip_address_check.html', votes=votes, competition_id=competition_id, competitions_for_select=competitions_for_select)
          
    return render_template('ip_address_check.html', competitions_for_select=competitions_for_select)
    
@app.route('/all_competitions', methods=['GET', 'POST'])
def all_competitions():
    user_role = session['role']
    if request.method == 'POST':
        if request.form.get('finalize_result') == 'true':
            competition_id = request.form.get('competition_id')
            if competition_id:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('UPDATE competitions SET result_finalised = 1 WHERE competition_id = %s', (competition_id,))
                conn.commit()
                conn.close()
                # Fetch the updated lists
                current_competitions = fetch_public_current_competitions()
                past_competitions = fetch_public_past_competitions()
                future_competitions = fetch_public_future_competitions()
                unfinalised_competitions = fetch_public_unfinalised_competitions()
                # Set success message
                flash('Competition result has been finalized.', 'success')
                # Render the template with the updated competition lists
                return render_template(
                    'all_competitions.html', 
                    user_role=user_role, 
                    current_competitions=current_competitions, 
                    past_competitions=past_competitions, 
                    future_competitions=future_competitions,
                    unfinalised_competitions = unfinalised_competitions
                )
        
    current_competitions = fetch_public_current_competitions()
    past_competitions = fetch_public_past_competitions()
    future_competitions = fetch_public_future_competitions()
    unfinalised_competitions = fetch_public_unfinalised_competitions()
    return render_template(
        'all_competitions.html', 
        user_role=user_role, 
        current_competitions=current_competitions, 
        past_competitions=past_competitions, 
        future_competitions=future_competitions,
        unfinalised_competitions = unfinalised_competitions
    )

@app.route('/votes_by_ip')
def votes_by_ip():
    ip_address = request.args.get('ip_address')
    competition_id = request.args.get('competition_id')
    votes_from_ip = []
    competition_name = None
    is_invalid = False

    is_invalid = vote_status_check(ip_address, competition_id)
    votes_from_ip, competition_name, user_status= fetch_votes_by_ip(ip_address, competition_id)
    
    return render_template('ip_address_votes.html', votes=votes_from_ip, ip_address=ip_address, competition_id=competition_id, competition_name=competition_name, is_invalid=is_invalid, user_status=user_status)

@app.route('/mark_votes_invalid', methods=['POST'])
def mark_votes_invalid():
    ip_address = request.form.get('ip_address')
    competition_id = request.form.get('competition_id')
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    update_query = """
        UPDATE votes
        SET status = 'invalid'
        WHERE ip_address = %s AND competition_id = %s AND status = 'valid'
    """
    cursor.execute(update_query, (ip_address, competition_id))
    connection.commit()
    
    cursor.close()
    connection.close()
    flash('Votes from this IP address have been set as invalid.','success')
    
    return redirect(url_for('votes_by_ip', ip_address=ip_address, competition_id=competition_id, is_invalid=True))

@app.route('/deactivate_users_by_ip', methods=['POST'])
def deactivate_users_by_ip():
    ip_address = request.form.get('ip_address')
    competition_id = request.form.get('competition_id')
    
    connection = get_db_connection()
    cursor = connection.cursor()

    select_users_query = """
        SELECT user_id
        FROM votes
        WHERE ip_address = %s AND competition_id = %s
    """
    cursor.execute(select_users_query, (ip_address, competition_id))
    user_list = cursor.fetchall()
    user_id_list = [row[0] for row in user_list]
    
    deactivate_query = """
        UPDATE users
        SET status = 'inactive'
        WHERE user_id IN (%s)
    """ % ',' .join(['%s'] * len(user_id_list))
    cursor.execute(deactivate_query, user_id_list)
    connection.commit()
    
    cursor.close()
    connection.close()
    flash('Users who vote from this invalid IP address have been set as inactive.','success')
    return redirect(url_for('votes_by_ip', ip_address=ip_address, competition_id=competition_id, is_invalid=True))

@app.route('/scrutineer/competitions_details/<int:competition_id>')
def scrutineer_competition_details(competition_id):
    # Use helper methods in query_competitions to fetch competitions
    competition = fetch_competition_by_competition_id(competition_id)
    user_role = session.get('role', None)
    return render_template('scrutineer_competition_details.html', user_role = user_role, competition=competition)
