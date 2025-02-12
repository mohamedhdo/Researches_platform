import mysql.connector
from flask import Flask, request, session, jsonify
from flask_bcrypt import Bcrypt
from flask_session import Session


app=Flask(__name__)


bcrypt = Bcrypt(app)

app.secret_key = 'SECRET'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql',
    'database': 'research'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route('/')
def index():
    return 'hello'



@app.route('/register',methods=['POST'])
def register():
    data=request.json
    first_name=data['first_name']
    last_name=data['last_name']
    email=data['email']
    password=data['password']
    if not all([first_name, last_name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    hashed_password=bcrypt.generate_password_hash(password).decode('utf-8')

    c=get_db_connection()
    cursor=c.cursor()

    try:
        cursor.execute('INSERT INTO RESEARCHER (first_name,last_name,email,password) VALUES (%s,%s,%s,%s)',(first_name,last_name,email,hashed_password))
        c.commit()
        return jsonify({"message": "Registration successful"}), 201
    except mysql.connector.IntegrityError:
        return jsonify("error:Email already exists"),409
    finally:
        cursor.close()
        c.close()

@app.route('/login',methods=['POST'])
def login():
    data=request.json
    email=data['email']
    password=data['password']

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    c = get_db_connection()
    cursor = c.cursor(dictionary=True)

    cursor.execute(f'SELECT * FROM RESEARCHER WHERE email=%s',(email,))
    user=cursor.fetchone()

    cursor.close()
    c.close()

    if user and bcrypt.check_password_hash(user['password'],password):
        session['user_id']=user['researcher_id']
        session['username'] = f'{user["first_name"]}_{user["last_name"]}'
        return jsonify(
            {"message": "Login successful", "user": {"id": user['researcher_id'], "name": user['first_name']}}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200








if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)

