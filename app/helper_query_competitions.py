from datetime import datetime

from flask import session
from app.db import get_db_connection

# Helper methods to fetch past & current & future competitions that are public to users, 
# and fetch specific competition by competition id
def fetch_public_past_competitions():
    query_public_past_competitions = """
        SELECT 
            c.competition_id,
            c.title AS competition_title,
            c.category AS competition_category,
            c.competition_description,
            c.start_date,
            c.end_date,
            c.competition_image,
            c.result_finalised,
            com.competitor_id,
            com.competitor_name,
            com.competitor_description,
            com.competitor_image,
            COUNT(CASE WHEN v.status = 'valid' THEN v.vote_id END) AS votes_quantity
        FROM 
            competitions c
        LEFT JOIN 
            competitors com ON c.competition_id = com.competition_id
        LEFT JOIN 
            votes v ON com.competitor_id = v.competitor_id
        WHERE
            c.end_date < NOW() AND 
            c.result_finalised AND 
            c.is_public = 1
        GROUP BY 
            c.competition_id, 
            com.competitor_id
        ORDER BY 
            c.start_date DESC, 
            com.competitor_name;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query_public_past_competitions)
    data = cursor.fetchall()

    public_past_competitions = {}
    for row in data:
        competition_id = row['competition_id']
        if competition_id not in public_past_competitions:
            public_past_competitions[competition_id] = {
                'competition_title': row['competition_title'],
                'competition_category': row['competition_category'],
                'competition_description': row['competition_description'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'competition_image': row['competition_image'],
                'result_finalised': row['result_finalised'],
                'competitors': []
            }
        competitor = {
            'competitor_id': row['competitor_id'],
            'competitor_name': row['competitor_name'],
            'competitor_description': row['competitor_description'],
            'competitor_image': row['competitor_image'],
            'votes_quantity': row['votes_quantity']
        }
        public_past_competitions[competition_id]['competitors'].append(competitor)

    cursor.close()
    conn.close()

    return public_past_competitions

def fetch_public_current_competitions():
    query_public_current_competitions = """
        SELECT 
            c.competition_id,
            c.title AS competition_title,
            c.category AS competition_category,
            c.competition_description,
            c.start_date,
            c.end_date,
            c.competition_image,
            c.result_finalised,
            com.competitor_id,
            com.competitor_name,
            com.competitor_description,
            com.competitor_image,
            COUNT(CASE WHEN v.status = 'valid' THEN v.vote_id END) AS votes_quantity
        FROM 
            competitions c
        LEFT JOIN 
            competitors com ON c.competition_id = com.competition_id
        LEFT JOIN 
            votes v ON com.competitor_id = v.competitor_id
        WHERE
            c.start_date <= NOW() AND c.end_date >= NOW()  AND
            c.is_public = 1 AND
            c.result_finalised = 0
        GROUP BY 
            c.competition_id, 
            com.competitor_id
        ORDER BY 
            c.start_date DESC, 
            com.competitor_name;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query_public_current_competitions)
    data = cursor.fetchall()

    public_current_competitions = {}
    for row in data:
        competition_id = row['competition_id']
        if competition_id not in public_current_competitions:
            public_current_competitions[competition_id] = {
                'competition_title': row['competition_title'],
                'competition_category': row['competition_category'],
                'competition_description': row['competition_description'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'competition_image': row['competition_image'],
                'result_finalised': row['result_finalised'],
                'competitors': []
            }
        competitor = {
            'competitor_id': row['competitor_id'],
            'competitor_name': row['competitor_name'],
            'competitor_description': row['competitor_description'],
            'competitor_image': row['competitor_image'],
            'votes_quantity': row['votes_quantity']
        }
        public_current_competitions[competition_id]['competitors'].append(competitor)

    cursor.close()
    conn.close()

    return public_current_competitions

def fetch_public_future_competitions():
    query_public_future_competitions = """
        SELECT 
            c.competition_id,
            c.title AS competition_title,
            c.category AS competition_category,
            c.competition_description,
            c.start_date,
            c.end_date,
            c.competition_image,
            c.result_finalised,
            com.competitor_id,
            com.competitor_name,
            com.competitor_description,
            com.competitor_image,
            COUNT(CASE WHEN v.status = 'valid' THEN v.vote_id END) AS votes_quantity
        FROM 
            competitions c
        LEFT JOIN 
            competitors com ON c.competition_id = com.competition_id
        LEFT JOIN 
            votes v ON com.competitor_id = v.competitor_id
        WHERE
            c.start_date > NOW()  AND
            c.is_public = 1
        GROUP BY 
            c.competition_id, 
            com.competitor_id
        ORDER BY 
            c.start_date DESC, 
            com.competitor_name;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query_public_future_competitions)
    data = cursor.fetchall()

    public_future_competitions = {}
    for row in data:
        competition_id = row['competition_id']
        if competition_id not in public_future_competitions:
            public_future_competitions[competition_id] = {
                'competition_title': row['competition_title'],
                'competition_category': row['competition_category'],
                'competition_description': row['competition_description'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'competition_image': row['competition_image'],
                'result_finalised': row['result_finalised'],
                'competitors': []
            }
        competitor = {
            'competitor_id': row['competitor_id'],
            'competitor_name': row['competitor_name'],
            'competitor_description': row['competitor_description'],
            'competitor_image': row['competitor_image'],
            'votes_quantity': row['votes_quantity']
        }
        public_future_competitions[competition_id]['competitors'].append(competitor)

    cursor.close()
    conn.close()

    return public_future_competitions

def fetch_public_unfinalised_competitions():
    query_public_unfinalised_competitions = """
        SELECT 
            c.competition_id,
            c.title AS competition_title,
            c.category AS competition_category,
            c.competition_description,
            c.start_date,
            c.end_date,
            c.competition_image,
            c.result_finalised,
            com.competitor_id,
            com.competitor_name,
            com.competitor_description,
            com.competitor_image,
            COUNT(CASE WHEN v.status = 'valid' THEN v.vote_id END) AS votes_quantity
        FROM 
            competitions c
        LEFT JOIN 
            competitors com ON c.competition_id = com.competition_id
        LEFT JOIN 
            votes v ON com.competitor_id = v.competitor_id
        WHERE
            c.end_date < NOW() AND 
            c.result_finalised = 0 AND 
            c.is_public = 1
        GROUP BY 
            c.competition_id, 
            com.competitor_id
        ORDER BY 
            c.start_date DESC, 
            com.competitor_name;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query_public_unfinalised_competitions)
    data = cursor.fetchall()

    public_unfinalised_competitions = {}
    for row in data:
        competition_id = row['competition_id']
        if competition_id not in public_unfinalised_competitions:
            public_unfinalised_competitions[competition_id] = {
                'competition_title': row['competition_title'],
                'competition_category': row['competition_category'],
                'competition_description': row['competition_description'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'competition_image': row['competition_image'],
                'result_finalised': row['result_finalised'],
                'competitors': []
            }
        competitor = {
            'competitor_id': row['competitor_id'],
            'competitor_name': row['competitor_name'],
            'competitor_description': row['competitor_description'],
            'competitor_image': row['competitor_image'],
            'votes_quantity': row['votes_quantity']
        }
        public_unfinalised_competitions[competition_id]['competitors'].append(competitor)

    cursor.close()
    conn.close()

    return public_unfinalised_competitions

def fetch_competitions_for_select():
    query_competitions_for_select = """
        SELECT 
            c.competition_id,
            c.title AS competition_title,
            c.category AS competition_category,
            c.competition_description,
            c.start_date,
            c.end_date,
            c.competition_image,
            c.result_finalised,
            com.competitor_id,
            com.competitor_name,
            com.competitor_description,
            com.competitor_image,
            COUNT(CASE WHEN v.status = 'valid' THEN v.vote_id END) AS votes_quantity
        FROM 
            competitions c
        LEFT JOIN 
            competitors com ON c.competition_id = com.competition_id
        LEFT JOIN 
            votes v ON com.competitor_id = v.competitor_id
        WHERE
            c.is_public = 1 AND
            c.result_finalised = 0
        GROUP BY 
            c.competition_id, 
            com.competitor_id
        ORDER BY 
            c.start_date DESC, 
            com.competitor_name;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query_competitions_for_select)
    data = cursor.fetchall()

    competitions_for_select = {}
    for row in data:
        competition_id = row['competition_id']
        if competition_id not in competitions_for_select:
            competitions_for_select[competition_id] = {
                'competition_title': row['competition_title'],
                'competition_category': row['competition_category'],
                'competition_description': row['competition_description'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'competition_image': row['competition_image'],
                'result_finalised': row['result_finalised'],
                'competitors': []
            }
        competitor = {
            'competitor_id': row['competitor_id'],
            'competitor_name': row['competitor_name'],
            'competitor_description': row['competitor_description'],
            'competitor_image': row['competitor_image'],
            'votes_quantity': row['votes_quantity']
        }
        competitions_for_select[competition_id]['competitors'].append(competitor)

    cursor.close()
    conn.close()
    return competitions_for_select

def fetch_competition_by_competition_id(competition_id):
    query_competition_by_competition_id = """
    SELECT 
        c.competition_id,
        c.title AS competition_title,
        c.category AS competition_category,
        c.competition_description,
        c.start_date,
        c.end_date,
        c.competition_image,
        c.result_finalised,
        com.competitor_id,
        com.competitor_name,
        com.competitor_description,
        com.competitor_image,
        COUNT(CASE WHEN v.status = 'valid' THEN v.vote_id END) AS votes_quantity
    FROM 
        competitions c
    LEFT JOIN 
        competitors com ON c.competition_id = com.competition_id
    LEFT JOIN 
        votes v ON com.competitor_id = v.competitor_id
    WHERE
        c.competition_id = %s AND
        c.is_public = 1
    GROUP BY 
        c.competition_id, 
        com.competitor_id;
    """

    user_id = session.get('user_id', None)
    query_if_user_voted = "SELECT * FROM votes WHERE user_id = %s AND competition_id = %s"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query_competition_by_competition_id,(competition_id,))
    competition = cursor.fetchall()

    cursor.execute(query_if_user_voted, (user_id, competition_id))
    user_has_voted = cursor.fetchone() is not None
    cursor.close()
    conn.close()

    competition_details = {}
    total_votes = 0
    max_votes = 0
    winners = []

    for row in competition:
        if row['competition_id'] not in competition_details:
            competition_details[row['competition_id']] = {
                'competition_title': row['competition_title'],
                'competition_category': row['competition_category'],
                'competition_description': row['competition_description'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'competition_image': row['competition_image'],
                'result_finalised': row['result_finalised'],
                'competitors': [],
                'is_ongoing': row['end_date'] >= datetime.now(),
                'user_has_voted': user_has_voted
            }
        competitor = {
            'competitor_id': row['competitor_id'],
            'competitor_name': row['competitor_name'],
            'competitor_description': row['competitor_description'],
            'competitor_image': row['competitor_image'],
            'votes_quantity': row['votes_quantity']
        }
        competition_details[row['competition_id']]['competitors'].append(competitor)

        total_votes += row['votes_quantity']

        if row['votes_quantity'] > max_votes:
            max_votes = row['votes_quantity']
            winners = [competitor]
        elif row['votes_quantity'] == max_votes:
            winners.append(competitor)
    
    competition_details[row['competition_id']]['total_votes'] = total_votes
    competition_details[row['competition_id']]['winners'] = winners

    return competition_details


def fetch_public_competitions():
    query = "SELECT competition_id, title FROM competitions WHERE is_public = 1 AND end_date >= CURDATE()"
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    competitions = cursor.fetchall()
    cursor.close()
    conn.close()
    return competitions

def fetch_competition_start_date(competition_id):
    query = "SELECT start_date FROM competitions WHERE competition_id = %s"
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (competition_id,))
    start_date = cursor.fetchone()
    cursor.close()
    conn.close()

    if start_date and 'start_date' in start_date:
        return start_date['start_date'].strftime('%Y-%m-%d')
    return None

def fetch_votes_for_competition(competition_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query_votes_for_competition = """
    SELECT 
        c.competitor_name, 
        u.username, 
        v.ip_address, 
        v.voted_at
    FROM 
        votes v
    JOIN 
        competitors c ON v.competitor_id = c.competitor_id
    JOIN 
        users u ON v.user_id = u.user_id
    WHERE 
        v.competition_id = %s
    """
    cursor.execute(query_votes_for_competition, (competition_id,))
    votes = cursor.fetchall()
    conn.close()
    return votes


def update_admin_user(username, hashed_password, email, first_name, last_name, location, profile_image_filename, user_description, role, status):
    # Construct the base update query
    query = "UPDATE users SET "
    params = []
    
    # Add each field to the query if it is provided    
    if hashed_password is not None:
        query += "password_hash = %s, "
        params.append(hashed_password)
    if email is not None:
        query += "email = %s, "
        params.append(email)
    if first_name is not None:
        query += "first_name = %s, "
        params.append(first_name)
    if last_name is not None:
        query += "last_name = %s, "
        params.append(last_name)
    if location is not None:
        query += "location = %s, "
        params.append(location)
    if profile_image_filename is not None:
        query += "user_image = %s, "
        params.append(profile_image_filename)
    if user_description is not None:
        query += "user_description = %s, "
        params.append(user_description)
    if role is not None:
        query += "role = %s, "
        params.append(role)
    if status is not None:
        query += "status = %s, "
        params.append(status)
    
    # Remove the trailing comma and space
    query = query.rstrip(", ")
    query += " WHERE username = %s"
    params.append(username)
    
    # Execute the query
    try:
        print(query)
        print(params)
        conn = get_db_connection()  # Replace with your database connection logic
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def get_only_future_competition():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)    
    # Fetch all competitions
    cursor.execute('SELECT *FROM competitions WHERE is_public = 0  ORDER BY start_date DESC')
    competitions = cursor.fetchall()
    return competitions

def get_only_future_competitors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch all competitors
    query = """SELECT competitor.*, comp.title AS competition_title
                FROM competitors AS competitor
                JOIN competitions AS comp
                ON competitor.competition_id = comp.competition_id
                WHERE comp.is_public = 0
                ORDER BY comp.start_date DESC;"""
    
    cursor.execute(query)
    competitors = cursor.fetchall()
    return competitors

def get_searched_future_competitors(search):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch all competitors
    query = """
            SELECT competitor.*, comp.title AS competition_title
            FROM competitors AS competitor
            JOIN competitions AS comp
            ON competitor.competition_id = comp.competition_id
            WHERE comp.is_public = 0
            AND (competitor.competitor_name LIKE %s OR competitor.competitor_description LIKE %s)
            ORDER BY comp.start_date DESC;
            """

    # Parameters for the query
    param = ('%' + search + '%', '%' + search + '%',)
    cursor.execute(query, param)
    competitors = cursor.fetchall()
    return competitors