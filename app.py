from flask import Flask, render_template_string, request, redirect, url_for, session
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import mysql.connector
import pandas as pd
import re
from flask_login import login_required, current_user ,  LoginManager, login_user, logout_user
import smtplib
from email.mime.text import MIMEText
from flask_login import UserMixin 
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Name of your login route

# Database Configuration for XAMPP
db = mysql.connector.connect(
    host="localhost",        # XAMPP runs on localhost
    user="root",             # Default MySQL user for XAMPP
    password="",             # Default is empty unless you set it
    database="stay_on_track" # Name of your database
)

admin_credentials = {
    'full_name': 'Admin',
    'username': 'admin11',
    'email': 'admin11@gmail.com',
    'password': '123'
}

@login_manager.user_loader
def load_user(id):
    return User.get(id)  # Adjust based on how your User class loads users

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        # Connect to DB and fetch user by ID
        # Return an instance of User if found
        pass

def calculate_dropout_risk(attendance, behavior, total_kt, cgpa):
    # Assign behavior score
    behavior_scores = {
        'Excellent': 0,
        'Good': 10,
        'Bad': 25,
        'Very Bad': 40
    }

    # Normalize and weigh factors
    risk = 0
    risk += (100 - attendance) * 0.3
    risk += behavior_scores.get(behavior, 20)
    risk += (total_kt * 10)  # assuming each KT increases risk by 10%
    
    if total_kt == 0:
        risk += (10 - cgpa) * 2  # high CGPA reduces risk
    else:
        risk += 20  # penalty for CGPA if KT exists and CGPA shouldn't be counted

    # Clamp between 0 and 100
    risk = max(0, min(100, round(risk)))
    return risk

def send_email_to_educator(student_name, risk):
    sender = 'fakebodies1@gmail.com'
    receiver = 'rushikeshgadkari60@gmail.com'
    subject = f"[Early Warning] Dropout Risk Detected for {student_name}"
    body = f"Dear Educator,\n\nThe dropout risk assessment for student {student_name} indicates a risk level of {risk}%. Please consider taking appropriate steps to support the student.\n\nBest regards,\nStayOnTrack Early Warning System"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(sender, 'adndzcchwakemzot')  # use app password here
            smtp.sendmail(sender, receiver, msg.as_string())
            print("Email sent to educator.")
    except Exception as e:
        print("Failed to send email:", e)

@app.route('/ai-system')
@login_required
def ai_system():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="stay_on_track"
    )
    cursor = conn.cursor(dictionary=True)

    # Fetch semester data for current user
    cursor.execute("SELECT * FROM semester_data WHERE student_name = %s", (current_user.username,))
    data = cursor.fetchone()

    if not data:
        return render_template_string("ai_result.html", message="No semester data found.")

    attendance = int(data['attendance'])
    behavior = data['behavior']
    total_kt = int(data['total_kts'])
    cgpa = float(data['cgpa']) if data['cgpa'] != '--' else 0.0


    risk = calculate_dropout_risk(attendance, behavior, total_kt, cgpa)

    # Send email to educator
    send_email_to_educator(current_user.username, risk)

    return render_template_string(AI_Predictor_html, risk=risk)


css = """
<style>
    body {
        margin: 0;
        font-family: 'Poppins', sans-serif;
        background: #0f172a;
        color: #e2e8f0;
    }

    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 50px;
        background: #020617;
    }

    header h1 {
        margin: 0;
        color: #38bdf8;
    }

    nav a {
        margin-left: 15px;
        text-decoration: none;
        color: #e2e8f0;
        padding: 8px 15px;
        border-radius: 8px;
        transition: 0.3s;
    }

    nav a:hover {
        background: #38bdf8;
        color: black;
    }

    .container {
        max-width: 900px;
        margin: 40px auto;
        padding: 20px;
    }

    .card {
        background: #1e293b;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    }

    input, select {
        width: 100%;
        padding: 10px;
        margin: 10px 0;
        border-radius: 8px;
        border: none;
        background: #0f172a;
        color: white;
    }

    button {
        width: 100%;
        padding: 12px;
        background: #38bdf8;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        cursor: pointer;
    }

    button:hover {
        background: #0ea5e9;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th, td {
        padding: 12px;
        border-bottom: 1px solid #334155;
        text-align: center;
    }

    th {
        background: #1e293b;
    }

    footer {
        text-align: center;
        padding: 20px;
        background: #020617;
        color: #64748b;
        margin-top: 40px;
    }
</style>
"""


home_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StayOnTrack</title>

    <!-- Google Font -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;600&display=swap" rel="stylesheet">

    <style>
        body {
            margin: 0;
            font-family: 'Poppins', sans-serif;
            background: #0f172a;
            color: #e2e8f0;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 50px;
            background: #020617;
        }

        header h1 {
            margin: 0;
            color: #38bdf8;
        }

        nav a {
            margin-left: 15px;
            text-decoration: none;
            color: #e2e8f0;
            padding: 8px 15px;
            border-radius: 8px;
            transition: 0.3s;
        }

        nav a:hover {
            background: #38bdf8;
            color: black;
        }

        .hero {
            text-align: center;
            padding: 80px 20px;
        }

        .hero h2 {
            font-size: 40px;
            margin-bottom: 15px;
            color: #38bdf8;
        }

        .hero p {
            max-width: 600px;
            margin: auto;
            font-size: 16px;
            color: #94a3b8;
        }

        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            padding: 50px;
        }

        .card {
            background: #1e293b;
            padding: 25px;
            border-radius: 15px;
            transition: 0.3s;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        }

        .card h3 {
            color: #38bdf8;
        }

        .buttons {
            text-align: center;
            margin: 40px;
        }

        .buttons a {
            text-decoration: none;
            margin: 10px;
            padding: 12px 20px;
            background: #38bdf8;
            color: black;
            border-radius: 10px;
            font-weight: 500;
            transition: 0.3s;
        }

        .buttons a:hover {
            background: #0ea5e9;
        }

        footer {
            text-align: center;
            padding: 20px;
            background: #020617;
            margin-top: 40px;
            color: #64748b;
        }
    </style>
</head>

<body>

<header>
    <h1>StayOnTrack</h1>
    <nav>
        {% if not user %}
            <a href="/login">Login</a>
            <a href="/signup">Sign Up</a>
        {% else %}
            <a href="/profile">Profile</a>
            <a href="/logout">Logout</a>
        {% endif %}
    </nav>
</header>

<section class="hero">
    <h2>AI-Powered Student Dropout Prevention</h2>
    <p>
        StayOnTrack uses intelligent analytics to identify at-risk students early,
        enabling educators to take proactive steps and improve student success rates.
    </p>
</section>

<section class="features">
    <div class="card">
        <h3>AI Risk Detection</h3>
        <p>Analyze attendance, behavior, and academic performance to predict dropout risk.</p>
    </div>

    <div class="card">
        <h3>Smart Insights</h3>
        <p>Data-driven decisions for educators to intervene at the right time.</p>
    </div>

    <div class="card">
        <h3>Learning Support</h3>
        <p>Access educational tools and resources to boost student performance.</p>
    </div>

    <div class="card">
        <h3>Financial Assistance</h3>
        <p>Help students find scholarships and reduce financial barriers.</p>
    </div>
</section>

<div class="buttons">
    {% if user %}
        <a href="/ai-system">AI System</a>
        <a href="/mobile-app">Learning</a>
        <a href="/eligible">Financial</a>
        <a href="/community-learning-hub">Community</a>
    {% endif %}
</div>

<footer>
    © 2026 StayOnTrack • Built with Flask & MySQL
</footer>

</body>
</html>
"""

signup_html = """
<!DOCTYPE html>
<html>
<head>
<title>Sign Up</title>
{{ css | safe }}
</head>
<body>

<header>
    <h1>StayOnTrack</h1>
    <nav>
        <a href="/">Home</a>
        <a href="/login">Login</a>
    </nav>
</header>

<div class="container">
    <div class="card">
        <h2>Create Account</h2>
        <form method="POST">
            <input type="text" name="full_name" placeholder="Full Name" required>
            <input type="text" name="username" placeholder="Username" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign Up</button>
        </form>
    </div>
</div>

<footer>© 2026 StayOnTrack</footer>

</body>
</html>
"""

page_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>{{ title }}</title>
    {{ css | safe }}
</head>
<body>
    <header>
        <h1>{{ title }}</h1>
        <nav>
            <a href="/">Home</a>
        </nav>
    </header>

    <div class="page-content">
        <h2>{{ title }}</h2>
        <p>Welcome to the {{ title }} page.</p>
    </div>

    <footer>
        <p>&copy; 2025 StayOnTrack</p>
    </footer>
</body>
</html>
"""

login_html = """
<!DOCTYPE html>
<html>
<head>
<title>Login</title>
{{ css | safe }}
</head>
<body>

<header>
    <h1>StayOnTrack</h1>
    <nav>
        <a href="/">Home</a>
        <a href="/signup">Sign Up</a>
    </nav>
</header>

<div class="container">
    <div class="card">
        <h2>Login</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</div>

<footer>© 2026 StayOnTrack</footer>

</body>
</html>
"""

admin_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    {{ css | safe }}
</head>
<body>
    <header>
        <h1>Admin Panel</h1>
        <nav>
            <a href="/logout">Logout</a>
            <a href="/student-data">All Students Data</a>
        </nav>
    </header>
    <div class="form-container">
        <h2>Enter Student Username and Semester</h2>
        <form method="POST">
            <input type="text" name="student_name" placeholder="Username" required>
            <label for="semester">Current Semester:</label>
            <select name="semester" id="semester" required>
                <option value="1">Semester 1</option>
                <option value="2">Semester 2</option>
                <option value="3">Semester 3</option>
                <option value="4">Semester 4</option>
                <option value="5">Semester 5</option>
                <option value="6">Semester 6</option>
                <option value="7">Semester 7</option>
                <option value="8">Semester 8</option>
            </select>
            <button type="submit">Submit</button>
        </form>

        {% if message %}
        <p style="color: red; margin-top: 10px;">{{ message }}</p>
        {% endif %}

        {% if show_modify_button %}
        <form method="GET" action="{{ url_for('modify_semester_data') }}">
            <input type="hidden" name="student_name" value="{{ student_name }}">
            <input type="hidden" name="semester" value="{{ semester }}">
            <button type="submit">Modify Semester Data</button>
        </form>
        {% endif %}
        {% if show_modify %}
    <form method="GET" action="/modify_semester_data">
        <input type="hidden" name="student_name" value="{{ student_name }}">
        <input type="hidden" name="semester" value="{{ semester }}">
        <button type="submit">Modify Semester Data</button>
    </form>
{% endif %}

    </div>
</body>
</html>


"""

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") != admin_credentials["username"]:
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    message = ""
    show_modify = False
    student_name = ""
    semester = 0

    if request.method == 'POST':
        student_name = request.form.get('student_name')
        semester = int(request.form.get('semester'))

        if not student_name or not semester:
            message = "❌ Please provide both the student name and semester."
        else:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(%s)", (student_name.lower(),))
            student = cursor.fetchone()

            if not student:
                message = f"❌ Student '{student_name}' has not signed up yet."
            else:
                cursor.execute("SELECT * FROM semester_data WHERE LOWER(student_name) = LOWER(%s)", (student_name.lower(),))
                data = cursor.fetchall()
                if data:
                    message = f"ℹ️ Semester data for '{student_name}' already exists."
                    show_modify = True
                else:
                    return redirect(url_for('enter_multiple_semesters_data', student_name=student_name, semester=semester))
    
    return render_template_string(admin_html, css=css, message=message, show_modify=show_modify, student_name=student_name, semester=semester)




@app.route('/enter_multiple_semesters_data', methods=['GET', 'POST'])
def enter_multiple_semesters_data():
    student_name = request.args.get('student_name')
    semester = int(request.args.get('semester'))  # The current semester selected by admin
    message = ""
    kt_data = {}

    # Only allow entry for previous semesters (i.e., current semester - 1)
    previous_semesters = semester - 1
    if previous_semesters < 1:
        message = "❌ No previous semesters to enter data for."
        return render_template_string(semester_multiple_data_html, student_name=student_name, semester=semester, message=message, kt_data=kt_data)

    if request.method == 'POST':
        # Loop through each semester from 1 to the selected previous semester
        for i in range(1, previous_semesters + 1):
            attendance = request.form.get(f'attendance_{i}')
            behavior = request.form.get(f'behavior_{i}')
            total_subjects = request.form.get(f'total_subjects_{i}')
            total_kts = request.form.get(f'total_kts_{i}')  # Corrected column name
            cgpa = request.form.get(f'cgpa_{i}')
            
            # Ensure total_kts is an integer or default to 0 if None
            total_kts = int(total_kts) if total_kts else 0  # Convert total_kts to int, default to 0 if None

            # If KT is greater than zero, disable CGPA and store it as '--'
            if total_kts > 0:
                cgpa = '--'  # Store '--' for CGPA if there are KTs

            # Insert the data into the database
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO semester_data (student_name, semester, attendance, behavior, total_subjects, total_kts, cgpa)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (student_name, i, attendance, behavior, total_subjects, total_kts, cgpa))
            db.commit()

            # Store KT data to check for disabling CGPA in the form
            kt_data[i] = total_kts > 0  # Store whether there are KTs for that semester
    
        message = "✅ Semester data successfully entered for all selected semesters!"
    
    return render_template_string(semester_multiple_data_html, student_name=student_name, semester=semester, message=message, kt_data=kt_data) 




# HTML for entering multiple semester data
semester_multiple_data_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Enter Multiple Semester Data</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
        }

        header {
            background-color: #333;
            color: #fff;
            padding: 20px;
            text-align: center;
        }

        header nav {
            margin-top: 10px;
        }

        header nav a {
            color: #fff;
            margin: 0 15px;
            text-decoration: none;
            font-size: 16px;
        }

        .form-container {
            background-color: #fff;
            margin: 20px auto;
            padding: 20px;
            width: 80%;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .form-container h2 {
            text-align: center;
            font-size: 24px;
        }

        .form-container h3 {
            margin-top: 20px;
            font-size: 20px;
            color: #333;
        }

        .form-container label {
            display: block;
            margin: 10px 0 5px;
            font-size: 14px;
            color: #555;
        }

        .form-container input[type="number"], 
        .form-container select {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }

        .form-container input[type="number"]:disabled {
            background-color: #f1f1f1;
        }

        .form-container button {
            padding: 10px 20px;
            background-color: #ffeb3b;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 20px;
            width: 100%;
            font-size: 16px;
        }

        .form-container button:hover {
            background-color: #fdd835;
        }

        .form-container p {
            color: red;
            font-size: 14px;
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <header>
        <h1>Enter Data for Semesters 1 to {{ semester - 1 }}</h1>
        <nav>
            <a href="/admin_panel">Admin Panel</a>
            <a href="/student-data">All Students Data</a>
        </nav>
    </header>
    <div class="form-container">
        <h2>Enter Semester Data for {{ student_name }}</h2>
        <form method="POST">
            {% for i in range(1, semester) %}
                <h3>Semester {{ i }}</h3>
                
                <label for="attendance_{{ i }}">Attendance (%):</label>
                <input type="number" name="attendance_{{ i }}" min="0" max="100" required>
                
                <label for="behavior_{{ i }}">Behavior:</label>
                <select name="behavior_{{ i }}" required>
                    <option value="Excellent">Excellent</option>
                    <option value="Good">Good</option>
                    <option value="Bad">Bad</option>
                    <option value="Very Bad">Very Bad</option>
                </select>

                <label for="total_subjects_{{ i }}">Total Subjects:</label>
                <input type="number" name="total_subjects_{{ i }}" min="1" required>
                
                <label for="total_kts_{{ i }}">Total KTs:</label>
                <input type="number" name="total_kts_{{ i }}" min="0" required>
                
                <label for="cgpa_{{ i }}">CGPA:</label>
                <input type="number" step="0.01" name="cgpa_{{ i }}" min="0" max="10" >
                <br><br>
            {% endfor %}
            <button type="submit">Submit</button>
        </form>
        {% if message %}
        <p style="color: red; margin-top: 10px;">{{ message }}</p>
        {% endif %}
    </div>
</body>
</html>
"""




@app.route('/')
def home():
    user = session.get('username')
    return render_template_string(home_html, css=css, user=user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Regex to validate Gmail address
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
            return "Invalid email! Please use a valid @gmail.com address."

        cursor = db.cursor()
        try:
            sql = "INSERT INTO users (full_name, username, email, password) VALUES (%s, %s, %s, %s)"
            values = (full_name, username, email, password)
            cursor.execute(sql, values)
            db.commit()
            return redirect(url_for('home'))
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cursor.close()
    return render_template_string(signup_html, css=css)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == admin_credentials['username'] and password == admin_credentials['password']:
            session['username'] = username
            return redirect(url_for('admin_panel'))

        cursor = db.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = user['username']
                login_user(User(user['id'], user['username'], user['password']))
                return redirect(url_for('home'))
            else:
                return '''
                <html>
                    <head>
                        <style>
                            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                            .button { background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; margin-top: 20px; border-radius: 5px; }
                        </style>
                    </head>
                    <body>
                        <h2>User not found. Please sign up first.</h2>
                        <a href="/signup" class="button">Sign Up</a>
                    </body>
                </html>
            '''
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cursor.close()
    return render_template_string(login_html, css=css)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))



@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    cursor = db.cursor(dictionary=True)

    try:
        sql = "SELECT full_name, username, email, password FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()

        if user:
            profile_html = """
<!DOCTYPE html>
<html>
<head>
<title>Profile</title>
{{ css | safe }}
</head>
<body>

<header>
    <h1>StayOnTrack</h1>
    <nav>
        <a href="/">Home</a>
        <a href="/logout">Logout</a>
    </nav>
</header>

<div class="container">
    <div class="card">
        <h2>User Profile</h2>
        <p><strong>Name:</strong> {{ user['full_name'] }}</p>
        <p><strong>Username:</strong> {{ user['username'] }}</p>
        <p><strong>Email:</strong> {{ user['email'] }}</p>
    </div>
</div>

<footer>© 2026 StayOnTrack</footer>

</body>
</html>
"""
            return render_template_string(profile_html, css=css, user=user)
        else:
            return "User not found!"

    except mysql.connector.Error as err:
        return f"Error: {err}"

    finally:
        cursor.close()


@app.route('/mobile-app')
def mobile_app():
    mobile_app_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mobile Learning App</title>
        {{ css | safe }}
    </head>
    <body>
        <header>
            <h1>Mobile Learning App</h1>
            <nav>
                <a href="/">Home</a>
            </nav>
        </header>

        <div class="form-containerrr">
            <h2>Welcome to the Mobile Learning App</h2>
            <p>Enhance your learning experience with our mobile app. Features include:</p>
            <ul>
                <li><a href="https://play.google.com/store/apps/details?id=com.edurev">Interactive Quizzes App---Click here</a></li>
                <li>Live video tutorials</li>
                <li>Progress tracking</li>
            </ul>
            <p>Coming soon on iOS and Android!</p>
        </div>

        <footer>
            <p>&copy; 2025 StayOnTrack</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(mobile_app_html, css=css)



@app.route('/community-learning-hub')
def community_learning_hub():
    hub_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Community Learning Hub</title>
        {{ css | safe }}
    </head>
    <body>
        <header>
            <h1>Community Learning Hub</h1>
            <nav>
                <a href="/">Home</a>
            </nav>
        </header>

        <div class="form-containerrr">
            <h2>Welcome to the Community Learning Hub</h2>
            <p>Here, students and educators can collaborate, share resources, and participate in discussions.</p>
            <ul>
                <li><p>Provides career development courses, professional networking.  
                 Visit <a href="https://www.linkedin.com/learning/" target="_blank" rel="noopener noreferrer">LinkedIn Learning</a> for more resources.</p>
                 </li>
                <li>Shared Study Materials - <a href="https://classroom.google.com/" target="_blank" rel="noopener noreferrer">Google Classroom</a></li>

                <li>Free Online Mentorship Programs - <a href="https://www.learntobe.org/" target="_blank" rel="noopener noreferrer">Learn To Be</a></li>

                <li>Join Our Peer Learning Group - <a href="https://t.me/stay_on_track" target="_blank">Request to Join</a></li>


            </ul>
        </div>

        <footer>
            <p>&copy; 2025 StayOnTrack</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(hub_html, css=css)


@app.route('/modify_semester_data', methods=['GET', 'POST'])
def modify_semester_data():
    student_name = request.args.get('student_name')
    semester = int(request.args.get('semester'))
    message = ""

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM semester_data WHERE LOWER(student_name) = LOWER(%s)", (student_name.lower(),))
    existing_data = cursor.fetchall()

    # Build a dictionary of existing values by semester
    data_by_sem = {row['semester']: row for row in existing_data}
    kt_data = {i: data_by_sem.get(i, {}).get('total_kts', 0) > 0 for i in range(1, semester)}

    if request.method == 'POST':
        try:
            for i in range(1, semester):
                attendance = request.form.get(f'attendance_{i}')
                behavior = request.form.get(f'behavior_{i}')
                total_subjects = request.form.get(f'total_subjects_{i}')
                total_kts = request.form.get(f'total_kts_{i}')
                cgpa = request.form.get(f'cgpa_{i}') if int(total_kts) == 0 else None

                # Check if data exists
                cursor.execute("SELECT * FROM semester_data WHERE LOWER(student_name) = LOWER(%s) AND semester = %s", (student_name.lower(), i))
                row = cursor.fetchone()

                if row:
                    cursor.execute("""
                        UPDATE semester_data
                        SET attendance=%s, behavior=%s, total_subjects=%s, total_kts=%s, cgpa=%s
                        WHERE LOWER(student_name)=LOWER(%s) AND semester=%s
                    """, (attendance, behavior, total_subjects, total_kts, cgpa, student_name.lower(), i))
                else:
                    cursor.execute("""
                        INSERT INTO semester_data (student_name, semester, attendance, behavior, total_subjects, total_kts, cgpa)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (student_name, i, attendance, behavior, total_subjects, total_kts, cgpa))
            
            db.commit()
            message = "✅ Data updated successfully!"
        except Exception as e:
            db.rollback()
            message = f"❌ Error: {str(e)}"

    return render_template_string(
        semester_multiple_data_html,
        student_name=student_name,
        semester=semester,
        kt_data=kt_data,
        message=message
    )

@app.route('/student-data')
def student_data():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM semester_data")
    students = cursor.fetchall()
    
    return render_template_string(student_data_html, css=css, students=students)

student_data_html = """
<!DOCTYPE html>
<html>
<head>
<title>Student Data</title>
{{ css | safe }}
</head>
<body>

<header>
    <h1>StayOnTrack</h1>
    <nav>
        <a href="/admin_panel">Admin</a>
    </nav>
</header>

<div class="container">
    <div class="card">
        <h2>All Students Data</h2>

        {% if students %}
        <table>
            <tr>
                <th>Username</th>
                <th>Semester</th>
                <th>Attendance</th>
                <th>Behavior</th>
                <th>KTs</th>
                <th>CGPA</th>
            </tr>

            {% for s in students %}
            <tr>
                <td>{{ s.student_name }}</td>
                <td>{{ s.semester }}</td>
                <td>{{ s.attendance }}</td>
                <td>{{ s.behavior }}</td>
                <td>{{ s.total_kts }}</td>
                <td>{{ s.cgpa }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
            <p>No data found</p>
        {% endif %}

    </div>
</div>

<footer>© 2026 StayOnTrack</footer>

</body>
</html>
"""

AI_Predictor_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Dropout Risk Signal</title>
  <style>
    body {
      background-color: #121212;
      color: #ffffff;
      font-family: Arial, sans-serif;
      text-align: center;
      padding-top: 100px;
    }
    .home-btn {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #00ff99;
  color: #121212;
  padding: 10px 20px;
  text-decoration: none;
  font-weight: bold;
  border-radius: 12px;
  box-shadow: 0 0 10px #00ff99;
  transition: background-color 0.3s, color 0.3s;
}

    .home-btn:hover {
      background-color: #00cc7a;
      color: #ffffff;
    }
    .risk-box {
      background-color: #1e1e1e;
      border-radius: 20px;
      padding: 30px;
      display: inline-block;
      box-shadow: 0 0 10px #00ff99;
    }
    .risk-value {
      font-size: 48px;
      font-weight: bold;
      color: #00ff99;
    }
    .message {
      margin-top: 20px;
      font-size: 20px;
      color: #ff4c4c;
    }
  </style>
</head>
<body>
  <a class="home-btn" href="/">🏠 Home</a>
  {% if risk is defined %}
    <div class="risk-box">
      <h2>Dropout Risk Prediction</h2>
      <div class="risk-value">{{ risk }}%</div>
      <p class="message">
        {% if risk >= 75 %}
          🚨 High Risk! Immediate attention needed.
        {% elif risk >= 50 %}
          ⚠️ Moderate Risk. Monitor progress.
        {% else %}
          ✅ Low Risk. Keep up the good work!
        {% endif %}
      </p>
    </div>
  {% else %}
    <p class="message">{{ message }}</p>
  {% endif %}
</body>
</html>
"""


@login_manager.user_loader
def load_user(user_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(user['id'], user['username'], user['password'])
    return None

@app.route('/eligible', methods=['GET', 'POST'])
def eligibility_check():
    result = None
    if request.method == 'POST':
        income = int(request.form['income'])
        category = request.form['category']

        eligible = False
        if category == 'OPEN':
            eligible = income < 30000
        elif category == 'SC/ST':
            eligible = income < 100000
        elif category == 'OBC':
            eligible = income < 50000

        if eligible:
            return redirect(url_for('financial_support'))
        else:
            result = 'Not Eligible'

    return render_template_string(eligible_html, result=result, css=css)

eligible_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Income Eligibility Check</title>
    {{ css | safe }}
    <header>
            <h1>Financial Support Management</h1>
            <nav>
                <a href="/">Home</a>
            </nav>
        </header>
</head>
<div class="form-containerrr">
<body style="background-color: #121212; color: white; font-family: Arial; text-align: center; padding-top: 50px;">
    <h1>Eligibility Checker</h1>
    <form method="post">
        <label>Annual Income:</label><br>
        <input type="number" name="income" required><br><br>

        <label>Category:</label><br>
        <select name="category" required>
            <option value="OPEN">OPEN</option>
            <option value="OBC">OBC</option>
            <option value="SC/ST">SC/ST</option>
        </select><br><br>

        <input type="submit" value="Check Eligibility">
    </form>

    {% if result %}
        <h2 style="margin-top: 30px;">Result: {{ result }}</h2>
    {% endif %}
    </div>
</body>
</html>
"""

@app.route('/financial-support')
def financial_support():
    financial_support_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Support Management</title>
        {{ css | safe }}
    </head>
    <body>
        <header>
            <h1>Financial Support Management</h1>
            <nav>
                <a href="/">Home</a>
            </nav>
        </header>

        <div class="form-containerrr">
            <h2>Welcome to the Financial Support Management</h2>
            <p>This section help you to  find and apply for financial aid, scholarships, and government support to prevent dropouts due to financial constraints.</p>
            <ul>
                <li><a href="https://scholarships.gov.in/">NSP---Click here</a></li>
                  <li>
    <a href="https://factsmgt.com/products/financial-management/grant-aid-assessment/?utm_source=chatgpt.com" target="_blank">
      FACTS Grant & Aid Assessment: This platform streamlines the financial aid process with customizable applications, thorough eligibility verification, and robust reporting tools, enabling data-driven award decisions.
    </a>
  </li>
                
        </div>

        <footer>
            <p>&copy; 2025 StayOnTrack</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(financial_support_html, css=css)


if __name__ == '__main__':
    app.run(debug=True)