from app.db import get_db_connection


def fetch_daily_votes(competition_id, voted_at):
    query = """
    SELECT 
        DATE(voted_at) AS vote_date,
        COUNT(*) AS vote_count
    FROM 
        votes
    INNER JOIN
        users ON votes.user_id = users.user_id
    WHERE 
        competition_id = %s AND
        DATE(voted_at) = %s AND
        users.status = 'active'
    GROUP BY 
        DATE(voted_at)
    ORDER BY 
        DATE(voted_at);
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (competition_id, voted_at))
    daily_votes = cursor.fetchall()
    cursor.close()
    conn.close()
    return daily_votes


def fetch_votes_for_competition(competition_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query_votes_for_competition = """
    SELECT 
        c.competitor_name, 
        u.username, 
        v.ip_address, 
        v.voted_at,
        v.status,
        u.status as user_status
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

def fetch_suspicious_competitions(competition_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query_votes_for_competition = """
    SELECT v.*, c.competitor_name AS competitor_name, u.username, subquery.ip_vote_count
    FROM (
        SELECT ip_address, COUNT(ip_address) as ip_vote_count
        FROM votes
        WHERE competition_id = %s AND status = 'valid'
        GROUP BY ip_address
        HAVING COUNT(*) > 1
    ) as subquery
    JOIN votes v ON v.ip_address = subquery.ip_address
    JOIN competitors c ON v.competitor_id = c.competitor_id
    JOIN users u ON v.user_id = u.user_id
    WHERE v.competition_id = %s AND v.status = 'valid'
    ORDER BY subquery.ip_vote_count DESC, v.ip_address, v.voted_at
    """
    cursor.execute(query_votes_for_competition, (competition_id, competition_id))
    votes = cursor.fetchall()
    cursor.close()
    conn.close()
    return votes

def vote_status_check(ip_address, competition_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    status_query = """
        SELECT COUNT(*) > 0 AS is_invalid
        FROM votes
        WHERE ip_address = %s AND competition_id = %s AND status = 'invalid'
    """
    cursor.execute(status_query, (ip_address, competition_id))
    is_invalid = cursor.fetchone()['is_invalid']
    cursor.close()
    conn.close()

    return is_invalid

def fetch_votes_by_ip(ip_address, competition_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Query to fetch votes and competition name
    query = """
        SELECT v.competitor_id, v.user_id, v.ip_address, v.voted_at, 
               u.username, u.first_name, u.last_name, u.status, c.competitor_name, comp.title as competition_name
        FROM votes v
        JOIN users u ON v.user_id = u.user_id
        JOIN competitors c ON v.competitor_id = c.competitor_id
        JOIN competitions comp ON v.competition_id = comp.competition_id
        WHERE v.ip_address = %s AND v.competition_id = %s
    """
    cursor.execute(query, (ip_address, competition_id))
    votes_from_ip = cursor.fetchall()
    
    competition_name = None
    if votes_from_ip:
        competition_name = votes_from_ip[0]['competition_name']
        user_status = votes_from_ip[0]['status']
    
    cursor.close()
    connection.close()
    
    return votes_from_ip, competition_name, user_status
