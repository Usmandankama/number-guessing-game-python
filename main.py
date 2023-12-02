from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import random


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='number-guessing-game'
    )
    return conn
# Game route
@app.route('/game', methods=['GET', 'POST'])
def game():
    actual_number = random.randint(1, 20)
    print(actual_number)
    guess_count = 0;
    score = 0;
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        user_guess = int(request.form['guess'])
        if user_guess < 1 or user_guess > 20:
            flash('Please enter a number between 1 and 20.', 'error')
        else:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Generate a random number between 1 and 10
            # print(actual_number)
            if user_guess == actual_number:
                flash('Congratulations! You guessed the correct number!', 'success')
                guess_count = 0
                score+=1;
                # Increase user score in the database
                cursor.execute('UPDATE users SET score = score + 1 WHERE username = %s', (session['username'],))
                conn.commit()
            else:
                if guess_count < 10:
                    if user_guess > actual_number:
                        flash(f"Try a lower number",'error')
                        guess_count+1;
                    elif user_guess < actual_number:
                        flash(f"Try a higher number",'error')
                        guess_count+1;
                else:
                    flash(f"10 guesse made! The correct answer is {actual_number}" ,'error') 
            conn.close()
    return render_template('game.html', score=score)

# Home route (Index)
@app.route('/', methods = ['GET','POST'])
def index():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE username = %s', (session['username'],))
    user = cursor.fetchone()
    conn.close()
    return render_template('index.html', user=user)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            return redirect('/admin')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        print(user)
        conn.close()
        if user:
            session['username'] = user['username']
            return redirect('/')
        else:
            flash('Invalid username or password!', 'error')
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        conn.commit()
        conn.close()
        flash('Registration successful. Please login.', 'success')
        return redirect('/login')
    return render_template('register.html')


@app.route('/admin')
def admin():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    print()
    cursor.execute('SELECT username,score FROM users ORDER BY score DESC LIMIT 10')
    leaderboard = cursor.fetchall()     
    conn.close()
    return  render_template('admin.html',users=users,leaderboard=leaderboard)

@app.route('/contact')
def contact():
    return  render_template('contactus.html')

@app.route('/feedback')
def feedback():
    return  render_template('feedback.html')


@app.route('/leaderboard')
def leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT username,score FROM users ORDER BY score DESC LIMIT 10')
    result = cursor.fetchall()        
    conn.close()
    return render_template('leaderboard.html', leaderboard=result)

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)