from flask import flash, redirect, request, session, url_for
from app import app
from app.db import get_db_connection

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    competition_id = request.form.get('competition_id')
    competitor_id = request.form.get('competitor_id')
    user_id = session.get('user_id')
    user_ip = request.remote_addr

    if not user_id or not competitor_id or not competition_id:
        flash('Voting failed', 'danger')
        return redirect(url_for('competition_details', competition_id=competition_id))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO votes (competitor_id, competition_id, user_id, ip_address) VALUES (%s, %s, %s, %s)',
        (competitor_id, competition_id, user_id, user_ip)
    )
    conn.commit()

    # Fetch the voted competitor's name
    cursor.execute(
        'SELECT competitor_name FROM competitors WHERE competitor_id = %s',
        (competitor_id,)
    )
    competitor_name = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    flash('Voted successfully!', 'success')
    return redirect(url_for('competition_details', competition_id=competition_id, voted_competitor_name=competitor_name,user_voted=competitor_id))
