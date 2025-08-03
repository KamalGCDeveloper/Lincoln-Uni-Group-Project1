from app import app
from flask import render_template, redirect, url_for, request, session, flash
import os
from werkzeug.utils import secure_filename
from app.db import get_db_connection
from password_hash_generator import generate_hash, password_is_valid, verify_password
import re

@app.route('/profile', methods=['GET', 'POST'])
def profile():

    return render_template('profile.html')

@app.route('/profile/user_info', methods=['GET', 'POST'])
def user_info():
    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    connection.close()

    if request.method == 'GET':
        if user:
            return render_template('user_info.html', user=user)
        else:
            error_message = 'User not found!'
            return redirect(url_for('home'))
    else:
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        location = request.form['location']
        user_description = request.form['user_description']
        delete_image = 'delete_image' in request.form

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT user_id FROM users WHERE email = %s', (email,))
        email_existed = cursor.fetchone()

        if email_existed and email_existed['user_id'] != session['user_id']:
            flash('Email already exists!', 'danger')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'danger')
        else:
            filename = user['user_image']

            if delete_image:
                if filename:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    filename = None

            user_upload_image = request.files.get('user_image')
            if user_upload_image and not delete_image:
                filename = secure_filename(user_upload_image.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                user_upload_image.save(file_path)

                # Delete the previous profile image if it exists
                old_profile_image = request.form.get('current_user_image')
                if old_profile_image:
                    old_profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], old_profile_image)
                    if os.path.exists(old_profile_image_path):
                        os.remove(old_profile_image_path)
            else:
                filename = request.form.get('current_user_image')

            cursor.execute('''UPDATE users 
                              SET email=%s, first_name=%s, last_name=%s, location=%s, user_image=%s, user_description=%s
                              WHERE user_id=%s''', 
                              (email, first_name, last_name, location, filename, user_description, session['user_id']))
            conn.commit()

        
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
        updated_user = cursor.fetchone()
        conn.close()

        flash('User Information has been updated.', 'success')
        return render_template('user_info.html', user=updated_user)

@app.route('/profile/update_password', methods=['GET','POST'])
def update_password():
    if request.method == 'GET':
        return render_template('update_password.html')
    
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    current_password = request.form['current_password']
    password_hash = generate_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch the current stored password hash from the database
    cursor.execute('SELECT password_hash FROM users WHERE user_id=%s', (session['user_id'],))
    user = cursor.fetchone()
    current_stored_password = user['password_hash']

    # Verify if the current password matches the stored hash
    if not verify_password(current_password, current_stored_password):
        flash('Current password is incorrect.', 'danger')
    
    # Check if the new password matches the confirmation password
    elif password != confirm_password:
        flash('Password and confirm password do not match.', 'danger')
    
    # Check if the new password is in valid format 
    elif not password_is_valid(password):
        flash('Password must contain at least 8 characters with 1 capital letter, 1 small letter, and 1 number', 'danger')
    
    # Ensure the new password is not the same as the current password
    elif verify_password(password, current_stored_password):
        flash('New password must be different from the current password', 'danger')
    
    else:
        # Update the password in the database
        cursor.execute('UPDATE users SET password_hash=%s WHERE user_id=%s', (password_hash, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Password has been updated.', 'success')

    # Re-fetch user data for rendering profile page
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE user_id=%s', (session['user_id'],))
    updated_user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('update_password.html', user=updated_user)