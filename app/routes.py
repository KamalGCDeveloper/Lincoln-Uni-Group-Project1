from flask import render_template, redirect, url_for, request, session, flash, jsonify
from app import app
import os
from werkzeug.utils import secure_filename
from app.db import get_db_connection
from app.helper_query_competitions import fetch_public_current_competitions, fetch_public_future_competitions, fetch_public_past_competitions,update_admin_user,get_only_future_competition,get_only_future_competitors,get_searched_future_competitors
from password_hash_generator import generate_hash, verify_password, password_is_valid
import re
from datetime import date
from markupsafe import Markup


#This class define all the routes and perform operation for different types of users

# Home page route
@app.route('/')
def home():
    # Use helper methods in query_competitions to fetch competitions
    current_competitions = fetch_public_current_competitions()
    past_competitions = fetch_public_past_competitions()
    future_competitions = fetch_public_future_competitions()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    user_id = session.get('user_id')
    if user_id:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('home.html',user = user, current_competitions=current_competitions, past_competitions=past_competitions, future_competitions=future_competitions)
    
    return render_template('home.html', current_competitions=current_competitions, past_competitions=past_competitions, future_competitions=future_competitions)
   
# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    #define different types of routes 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        #check if the user is active or none
        if user is None:
            flash('Invalid username or password', 'danger')
        elif user['status'] != "active":
            flash('User is inactive.', 'danger')
        elif verify_password(password, user['password_hash']):
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            session['username'] = user['username']
            session['user_image'] = user['user_image']
            flash(Markup(f'Welcome back, <strong>{user["username"]}</strong>!'), 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
            return render_template('login.html', username=username)
    
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        location = request.form['location']
        user_image = request.files.get('user_image')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT user_id FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        cursor.execute('SELECT user_id FROM users WHERE email = %s', (email,))
        email_existed = cursor.fetchone()

        # If account exists show error and validation checks
        if account or email_existed:
            flash('User name/Email already exists!', 'danger')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'danger')
        elif not re.match(r'[A-Za-z0-9]+', username):
             flash('Username must contain only characters and numbers!', 'danger')
        elif password != confirm_password:
            flash('Password and confirm password do not match.', 'danger')
        elif not password_is_valid(password):
            flash('Password must contain atleast 8 character with 1 capital letter, 1 small letter and 1 number.', 'danger')
        else:
            hashed_password = generate_hash(password)#generate the hashed code for password
            user_image_filename = None
            if user_image: #if profile image exist
                user_image_filename = secure_filename(user_image.filename)
                file_path = app.config['UPLOAD_FOLDER'] + username + user_image_filename
                os.makedirs(os.path.dirname(file_path), exist_ok=True)        
                user_image.save(file_path)
                #profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_image_filename))

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password_hash, email, first_name, last_name, location, user_image, user_description, role,status) VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s)',
                (username, hashed_password, email, first_name, last_name, location, user_image, None, 'voter', 'active')
            )
            conn.commit()
            conn.close()
            flash('Registration successful, please log in.', 'success')
            return redirect(url_for('login'))
        # If there were errors, render the form again with the provided values
        return render_template('register.html', username=username, email=email)
    
    return render_template('register.html')

# Logout route perform session deletion
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('user_id', None)
        session.pop('role', None)
        session.pop('username', None)
        flash('You have been logged out.', 'success')
    else:
        flash('Invalid request method for logout.', 'danger')
    return redirect(url_for('home'))

# Dashboard for admin
@app.route('/admin_dashboard')
def admin_dashboard():
    
    return render_template('admin_dashboard.html')


#Create and update admin and scrutineer
@app.route('/create_users', methods=['GET', 'POST'])
@app.route('/create_users/<int:user_id>', methods=['GET', 'POST'])
def create_users(user_id=None):
    if request.method == 'POST':        
       
        username = request.form.get('username')
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        location = request.form.get('location')
        user_image = request.files.get('user_image')
        hashed_password = None
        # create user type and insert into database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT user_id FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        cursor.execute('SELECT user_id FROM users WHERE email = %s', (email,))
        email_existed = cursor.fetchone()
        conn.close()   
        #check for different action create and update users
        if request.form.get('action') == 'register':
            
            if  role.strip() == '' or role == 'Select a role':
                flash('No admin or scruinteer role has been selected', 'danger')
            else:                

                # If account exists show error and validation checks
                if account or email_existed:
                    flash('User name/Email already exists!', 'danger')
                elif not re.match(r'[A-Za-z0-9]+', username):
                    flash('Username must contain only characters and numbers!', 'danger')
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    flash('Invalid email address!', 'danger')                
                elif password != confirm_password:
                    flash('Password and confirm password do not match.', 'danger')
                elif not password_is_valid(password):
                    flash('Password must contain atleast 8 character with 1 capital letter, 1 small letter and 1 number.', 'danger')           
                elif role == 'Select a role' or role == '':
                    flash('No admin or scruinteer role has been selected', 'danger')
                else:
                    hashed_password = generate_hash(password)#generate the hashed code for password
                    user_image_filename = None
                    if user_image: #if profile image exist
                        user_image_filename = secure_filename(user_image.filename)
                        file_path = app.config['UPLOAD_FOLDER'] + username + user_image_filename
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)        
                        user_image.save(file_path)

                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO users (username, password_hash, email, first_name, last_name, location, user_image, user_description, role,status) VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s)',
                        (username, hashed_password, email, first_name, last_name, location, user_image, None, role, 'active')
                    )
                    conn.commit()
                    conn.close()
                    flash('Registration successful, please log in.', 'success')
            return render_template('admin_create_users.html')   
        
        elif request.form.get('action') == 'update':
            status = request.form['status']
            if password and confirm_password:
                hashed_password = None
                pass
            elif password != confirm_password:
                flash('Password and confirm password do not match.', 'danger')
            elif role == 'Select a role':
                flash('No admin or scruinteer role has been selected', 'danger')
            else:
                if password != None and password != '':
                    hashed_password = generate_hash(password)#generate the hashed code for password
                
                #Update the user details
                update_admin_user(username, hashed_password, email, first_name, last_name, location, user_image, None, role, status)
            
                flash('Admin updated user role successfully', 'success')
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users where username = %s", (username,))
            user = cursor.fetchone()
            conn.close()
            return render_template('admin_create_users.html', user = user)
            
    elif user_id and request.method == 'GET': # when the update user create is displayed
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users where user_id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('admin_create_users.html', user = user)        
    
    else: 
        #when new user is created 
        return render_template('admin_create_users.html')

#Create Competition
@app.route('/create_competition', methods=['GET', 'POST'])
def create_competition():
     if request.method == 'POST':
        title = request.form['title']
        category = request.form['categories']
        competition_description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO competitions (title, category, competition_description, start_date, end_date, is_public)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (title, category, competition_description, start_date, end_date, '0')) #0 means it's not public
        conn.commit()
        conn.close()
        
        flash('Competition created successfully!', 'success')
        
     return render_template('create_competition.html', current_date = date.today().isoformat())

#Create Competitors
@app.route('/create_competitors', methods=['GET', 'POST'])
def create_competitors():
    if request.method == 'POST':
        
        if request.form and request.form.get('action') == "pre_selected_competition":
            competition_id = request.form['competition_id']
            competitions = get_only_future_competition()
            return render_template('create_competitors.html', competitions=competitions, competition_id = competition_id)
        else:
            competition_id = request.form['competition_id']
            title = request.form['name']
            description = request.form['description']
            competitors_image = request.files['competitors_image']
            
            # Save the uploaded file
            if competitors_image:
                image_filename = secure_filename(competitors_image.filename)
                competitors_image.save(os.path.join(app.config['UPLOAD_COMP_FOLDER'], image_filename))
            else:
                image_filename = None

            # Insert into the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO competitors (competition_id, competitor_name, competitor_description, competitor_image)
                VALUES (%s, %s, %s, %s)
                ''',
                (competition_id, title, description, image_filename)
            )
            conn.commit()
            competitions = get_only_future_competition()
            flash('Competitors created successfully!', 'success')
            return render_template('create_competitors.html',competitions=competitions,  competition_id=competition_id)
    elif request.method == 'GET':
        
        competitions = get_only_future_competition()
        return render_template('create_competitors.html', competitions=competitions)

#View voters profile, delete, search, and update status
@app.route('/voters_profile', methods=['GET', 'POST'])
@app.route('/voters_profile/<int:user_id>', methods=['GET', 'POST'])
def voters_profile(user_id = None):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    action = request.form.get('action')
    
    
    if user_id is None and action == 'search':
        search_query = request.form.get('search_query', '')
        search_query = f"%{search_query}%"
        cursor.execute("SELECT * FROM users WHERE (username LIKE %s OR first_name LIKE %s OR last_name LIKE %s OR email LIKE %s) AND role = %s AND user_id != %s",
               (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%","voter", session.get('user_id'),))

        users = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return render_template('view_voters_profile.html', users=users)
    elif user_id is None and request.method == 'GET': #Display the voters list
        
        query = 'SELECT * FROM users where role = %s'
        params = ('voter',)        
        cursor.execute(query, params)
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return render_template('view_voters_profile.html', users=users)
    elif action == 'delete': # do delete action
        username = request.form['username']
        cursor.execute("Delete FROM users where username = %s", (username,))
        connection.commit()
        
        query = 'SELECT * FROM users where role = %s'
        params = ('voter',)        
        cursor.execute(query, params)
        users = cursor.fetchall()
        
        cursor.close()
        connection.close()
        flash('Admin deleted the user successfully', 'success')
        return render_template('view_voters_profile.html', users = users)
    
    elif action == 'update': # do update action
        username = request.form['username']
        status = request.form['status']
        cursor.execute("UPDATE users SET status = %s WHERE username = %s", (status, username))
        connection.commit()
        
        query = 'SELECT * FROM users where role = %s'
        params = ('voter',)        
        cursor.execute(query, params)
        users = cursor.fetchall()
        
        cursor.close()
        connection.close()
        flash('Admin updated user status successfully', 'success')
        return render_template('view_voters_profile.html', users = users)
    
    elif user_id:
        cursor.execute("SELECT * FROM users where user_id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('view_voters_profile_details.html', user = user)
    
#View admin, scrutineer profile
@app.route('/view_admin_scrutineer')
def view_admin_scrutineer():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users where role = %s or role = %s", ("admin","scrutineer",))
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('view_admin_scrutineer.html', users=users)

#update admin and scrutineer account
@app.route('/update_admin_users', methods=['GET', 'POST'])
def update_admin_users():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        location = request.form.get('location')
        user_description = request.form.get('user_description')
        role = request.form.get('role')
        status = request.form.get('status')
        profile_image = request.files.get('profile_image')
        # Hash password
        hashed_password = generate_hash(password)
        
        # Handle file upload
        profile_image_filename = None
        if profile_image and profile_image.filename:
            profile_image_filename = secure_filename(profile_image.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image_filename)
            profile_image.save(file_path)

        #Update the user details
        update_admin_user(username, hashed_password, email, first_name, last_name, location, profile_image_filename, user_description, role, status)
    
        flash('Admin updated user role successfully', 'success')
        #Query to get users list
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users where username = %s", (username,))
        users = cursor.fetchone()
        cursor.close()
        connection.close()
        return redirect(url_for('view_admin_scrutineer', users = users))
    
@app.route('/list_competitors', methods=['GET', 'POST'])
@app.route('/list_competitors/<int:competitor_id>', methods=['GET', 'POST'])
def list_competitors(competitor_id=None):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    action = request.form.get('action')
    
    if  action == 'search':
        search_query = request.form.get('search_query')
        competitors = get_searched_future_competitors(search_query)
        
        return render_template('manage_competitors.html', competitors=competitors, search_query = search_query)
    elif request.method == 'POST' and competitor_id:
        # Check if update or delete action
        if  action == 'update':
            # Update competitor
            competition_id = request.form['competition_id']
            competitor_name = request.form['name']
            competitor_description = request.form['description']
            competitor_image = request.files['competitors_image']
            # Update image if a new one is uploaded
            
            if competitor_image:
                image_filename = secure_filename(competitor_image.filename)
                competitor_image.save(os.path.join(app.config['UPLOAD_COMP_FOLDER'], image_filename))            
            else:
                image_filename = request.form['existing_image']
            query = '''
                UPDATE competitors 
                SET competition_id = %s, competitor_name = %s, competitor_description = %s, competitor_image = %s 
                WHERE competitor_id = %s
                '''
            cursor.execute(query, (competition_id, competitor_name, competitor_description, image_filename, competitor_id))
            connection.commit()
            cursor.close()
            connection.close()
        elif action == 'delete':
            # Delete competitor
            query = 'DELETE FROM competitors WHERE competitor_id = %s'
            cursor.execute(query, (competitor_id,))
            connection.commit()
            cursor.close()
            connection.close()
        return redirect(url_for('list_competitors'))
    
    elif request.method == 'GET' and competitor_id:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor = connection.cursor(dictionary=True)
        query = '''
            SELECT 
                c.competitor_id, 
                c.competitor_name, 
                c.competitor_description, 
                c.competitor_image, 
                c.competition_id, 
                comp.title AS competition_title
            FROM 
                competitors c
            LEFT JOIN 
                competitions comp ON c.competition_id = comp.competition_id
            WHERE 
                c.competitor_id = %s
        '''
        cursor.execute(query, (competitor_id,))
        competitor = cursor.fetchone()  
        
        
        competitions = get_only_future_competition()
    
        cursor.close()
        connection.close()

        return render_template('manage_competitors_details.html', competitor = competitor, competitions = competitions)
    elif request.method == 'GET':
        # Display the competitors list
        
        competitors = get_only_future_competitors()        
        return render_template('manage_competitors.html', competitors=competitors)
    
    cursor.close()
    connection.close()
    return redirect(url_for('list_competitors'))

@app.route('/delete_competitor/<int:competitor_id>', methods=['POST'])
def delete_competitor(competitor_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = 'DELETE FROM competitors WHERE competitor_id = %s'
    cursor.execute(query, (competitor_id,))
    connection.commit()
    cursor.close()
    connection.close()
    flash('Admin deleted competitor successfully', 'danger')
    return redirect(url_for('list_competitors'))



@app.route('/list_competitions')
def list_competitions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch all competitors
    cursor.execute('SELECT * FROM competitors')
    all_competitors = cursor.fetchall()   
    
    # Fetch all competitions
    competitions = get_only_future_competition()
    
    # Pass data to the template
    return render_template('admin_manage_competitions.html', competitions=competitions, all_competitors=all_competitors)

@app.route('/edit_competition', methods=['POST'])
def edit_competition():
    competition_id = request.form['competition_id']
    
    
    if  request.form.get('action') == 'public_competition':
            
        connection = get_db_connection()
        cursor = connection.cursor()
        sql = '''
        UPDATE competitions
        SET is_public=%s WHERE competition_id=%s
        '''
        cursor.execute(sql, ('1', competition_id,)) #make the competition public
        connection.commit()
        connection.close()
        flash('Competition is made public.', 'success')
    else:    
        title = request.form['title']
        category = request.form['category']
        description = request.form['competition_description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        sql = '''
            UPDATE competitions
            SET title=%s, category=%s, competition_description=%s, start_date=%s, end_date=%s
            WHERE competition_id=%s
        '''
        cursor.execute(sql, (title, category, description, start_date, end_date, competition_id))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Admin updated competition successfully', 'success')
    return redirect(url_for('list_competitions'))

@app.route('/delete_competition', methods=['POST'])
def delete_competition():
    competition_id = request.form.get('competition_id')

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM competitions WHERE competition_id=%s', (competition_id,))
    connection.commit()
    cursor.close()
    connection.close()
    flash('Admin deleted competition successfully', 'danger')
    return redirect(url_for('list_competitions'))

@app.route('/add_competitor_to_competition', methods=['POST'])
def add_competitor_to_competition():
    competition_id = request.form['competition_id']
    competitor_id = request.form['competitor_id']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE competitors SET competition_id=%s WHERE competitor_id=%s', (competition_id, competitor_id))
    connection.commit()
    cursor.close()
    connection.close()
    flash('Admin added competitor successfully', 'success')
    return jsonify({'success': True})

@app.route('/remove_competitor_from_competition', methods=['POST'])
def remove_competitor_from_competition():
    competition_id = request.form['competition_id']
    competitor_id = request.form['competitor_id']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM competitors WHERE competitor_id = %s AND competition_id = %s', (competitor_id, competition_id,))
    connection.commit()
    cursor.close()
    connection.close()
    flash('Admin removed competitor successfully', 'danger')
    return jsonify({'status': 'success'})