import mysql.connector
from flask import Flask, request, session, jsonify
from flask_bcrypt import Bcrypt
from flask_session import Session
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Check if user is logged in
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

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
        session['username'] = user["first_name"]
        return jsonify(
            {"message": "Login successful", "user": {"id": user['researcher_id'], "name": user['first_name']}}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200




######## UNIVERSITY CRUD ##############################

@app.route('/univ', defaults={'id': None})
@app.route('/univ/<int:id>')
def get_university(id):
    c=get_db_connection()
    cursor=c.cursor(dictionary=True)

    if id:
        cursor.execute('SELECT * FROM UNIVERSITY WHERE university_id=%s', (id,))
        university = cursor.fetchone()

        cursor.close()

        if university:
            return jsonify({"university": university}), 200
        else:
            return jsonify({"error": "University not found"}), 404

    cursor.execute('SELECT * FROM UNIVERSITY')
    universities=cursor.fetchall()

    cursor.close()
    c.close()
    return jsonify({"universities":universities})

@app.route('/univ/add',methods=['POST'])
@login_required
def add_university():
    data=request.json
    name=data.get('university_name')
    if not name:
        return jsonify({"error":"university_name field required"}),400
    c=get_db_connection()
    cursor=c.cursor(dictionary=True)
    try:
        cursor.execute('INSERT INTO UNIVERSITY (university_name) VALUES (%s)',(name,))
        c.commit()
        return jsonify({"message":"University added successfully"}),201
    except mysql.connector.IntegrityError:
        return jsonify({"error":"Error while inserting data "}),409
    finally:
        cursor.close()
        c.close()

@app.route('/univ/delete/<int:id>',methods=['DELETE'])
@login_required
def delete_university(id):
    c=get_db_connection()
    cursor=c.cursor()
    cursor.execute("DELETE FROM UNIVERSITY WHERE university_id=%s",(id,))
    c.commit()

    if cursor.rowcount==0:
        cursor.close()
        c.close()
        return jsonify({"message":"University not found"}),404

    cursor.close()
    c.close()


    return jsonify({"message":"University deleted successfully"}),204


@app.route('/univ/update/<int:id>', methods=['PUT'])
@login_required
def update_university(id):
    data = request.json
    new_name = data.get('university_name')

    if not new_name:
        return jsonify({"error": "university_name field required"}), 400

    c = get_db_connection()
    cursor = c.cursor(dictionary=True)


    cursor.execute("SELECT * FROM UNIVERSITY WHERE university_id = %s", (id,))
    university = cursor.fetchone()

    if not university:
        cursor.close()
        c.close()
        return jsonify({"error": "University not found"}), 404


    try:
        cursor.execute("UPDATE UNIVERSITY SET university_name = %s WHERE university_id = %s", (new_name, id))
        c.commit()
        return jsonify({"message": "University updated successfully"}), 200
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Error while updating university"}), 409
    finally:
        cursor.close()
        c.close()



#############FIELD CRUD###################

@app.route('/field', defaults={'id': None})
@app.route('/field/<int:id>')
def get_fields(id):
    c=get_db_connection()
    cursor=c.cursor(dictionary=True)

    if id:
        cursor.execute('SELECT * FROM FIELD WHERE field_id=%s',(id,))
        field=cursor.fetchone()

        cursor.close()

        if field:
            return jsonify({"field": field}), 200
        else:
            return jsonify({"error": "field not found"}), 404


    cursor.execute('SELECT * FROM FIELD')
    fields=cursor.fetchall()

    cursor.close()
    c.close()
    return jsonify({"fields":fields})

@app.route('/field/add',methods=['POST'])
@login_required
def add_field():
    data=request.json
    name=data.get('field_name')
    if not name:
        return jsonify({"error":"field_name field required"}),400
    c=get_db_connection()
    cursor=c.cursor(dictionary=True)
    try:
        cursor.execute('INSERT INTO FIELD (field_name) VALUES (%s)',(name,))
        c.commit()
        return jsonify({"message":"Field added successfully"}),201
    except mysql.connector.IntegrityError:
        return jsonify({"error":"Error while inserting data "}),409
    finally:
        cursor.close()
        c.close()

@app.route('/field/delete/<int:id>',methods=['DELETE'])
@login_required
def delete_field(id):
    c=get_db_connection()
    cursor=c.cursor()
    cursor.execute("DELETE FROM FIELD WHERE field_id=%s",(id,))
    c.commit()

    if cursor.rowcount==0:
        cursor.close()
        c.close()
        return jsonify({"message":"Field not found"}),404

    cursor.close()
    c.close()


    return jsonify({"message":"Field deleted successfully"}),204



@app.route('/field/update/<int:id>', methods=['PUT'])
@login_required
def update_field(id):
    data = request.json
    new_name = data.get('field_name')

    if not new_name:
        return jsonify({"error": "field_name field required"}), 400

    c = get_db_connection()
    cursor = c.cursor(dictionary=True)


    cursor.execute("SELECT * FROM FIELD WHERE field_id = %s", (id,))
    field = cursor.fetchone()

    if not field:
        cursor.close()
        c.close()
        return jsonify({"error": "Field not found"}), 404

    try:
        cursor.execute("UPDATE FIELD SET field_name = %s WHERE field_id = %s", (new_name, id))
        c.commit()
        return jsonify({"message": "Field updated successfully"}), 200
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Error while updating Field"}), 409
    finally:
        cursor.close()
        c.close()




############ CATEGORY CRUD ######################

@app.route('/category', defaults={'id': None})
@app.route('/category/<int:id>')
@login_required
def get_category(id):
    c = get_db_connection()
    cursor = c.cursor(dictionary=True)

    if id:
        cursor.execute('SELECT * FROM CATEGORY WHERE category_id=%s',(id,))
        category=cursor.fetchone()

        cursor.close()

        if category:
            return jsonify({"category": category}), 200
        else:
            return jsonify({"error": "Category not found"}), 404



    cursor.execute('SELECT * FROM CATEGORY')
    categories=cursor.fetchall()

    cursor.close()
    c.close()
    return jsonify({"categories":categories})

@app.route('/category/add',methods=['POST'])
@login_required
def add_category():
    data=request.json
    name=data.get('category_name')
    if not name:
        return jsonify({"error":"category_name field required"}),400
    c=get_db_connection()
    cursor=c.cursor(dictionary=True)
    try:
        cursor.execute('INSERT INTO CATEGORY (category_name) VALUES (%s)',(name,))
        c.commit()
        return jsonify({"message":"Category added successfully"}),201
    except mysql.connector.IntegrityError:
        return jsonify({"error":"Error while inserting data "}),409
    finally:
        cursor.close()
        c.close()

@app.route('/category/delete/<int:id>',methods=['DELETE'])
@login_required
def delete_category(id):
    c=get_db_connection()
    cursor=c.cursor()
    cursor.execute("DELETE FROM CATEGORY WHERE category_id=%s",(id,))
    c.commit()

    if cursor.rowcount==0:
        cursor.close()
        c.close()
        return jsonify({"message":"Category not found"}),404

    cursor.close()
    c.close()


    return jsonify({"message":"Category deleted successfully"}),204


@app.route('/category/update/<int:id>', methods=['PUT'])
@login_required
def update_category(id):
    data = request.json
    new_name = data.get('category_name')

    if not new_name:
        return jsonify({"error": "category_name field required"}), 400

    c = get_db_connection()
    cursor = c.cursor(dictionary=True)


    cursor.execute("SELECT * FROM CATEGORY WHERE category_id = %s", (id,))
    category = cursor.fetchone()

    if not category:
        cursor.close()
        c.close()
        return jsonify({"error": "Category not found"}), 404


    try:
        cursor.execute("UPDATE CATEGORY SET category_name = %s WHERE category_id = %s", (new_name, id))
        c.commit()
        return jsonify({"message": "Category updated successfully"}), 200
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Error while updating category"}), 409
    finally:
        cursor.close()
        c.close()














########## KEYWORD CRUD#######################################



@app.route('/keyword', defaults={'id': None})
@app.route('/keyword/<int:id>')
def get_keyword(id):
    c=get_db_connection()
    cursor=c.cursor(dictionary=True)

    if id:
        cursor.execute('SELECT * FROM KEYWORD WHERE keyword_id=%s', (id,))
        keyword = cursor.fetchone()

        cursor.close()

        if keyword:
            return jsonify({"keyword": keyword}), 200
        else:
            return jsonify({"error": "Keyword not found"}), 404

    cursor.execute('SELECT * FROM KEYWORD')
    keywords=cursor.fetchall()

    cursor.close()
    c.close()
    return jsonify({"keywords":keywords})

@app.route('/keyword/add',methods=['POST'])
@login_required
def add_keyword():
    data=request.json
    name=data.get('keyword_name')
    if not name:
        return jsonify({"error":"keyword_name field required"}),400
    c=get_db_connection()
    cursor=c.cursor(dictionary=True)
    try:
        cursor.execute('INSERT INTO KEYWORD (keyword_name) VALUES (%s)',(name,))
        c.commit()
        return jsonify({"message":"Keyword added successfully"}),201
    except mysql.connector.IntegrityError:
        return jsonify({"error":"Error while inserting data "}),409
    finally:
        cursor.close()
        c.close()

@app.route('/keyword/delete/<int:id>',methods=['DELETE'])
@login_required
def delete_keyword(id):
    c=get_db_connection()
    cursor=c.cursor()
    cursor.execute("DELETE FROM KEYWORD WHERE keyword_id=%s",(id,))
    c.commit()

    if cursor.rowcount==0:
        cursor.close()
        c.close()
        return jsonify({"message":"Keyword not found"}),404

    cursor.close()
    c.close()


    return jsonify({"message":"Keyword deleted successfully"}),204


@app.route('/keyword/update/<int:id>', methods=['PUT'])
@login_required
def update_keyword(id):
    data = request.json
    new_name = data.get('keyword_name')

    if not new_name:
        return jsonify({"error": "keyword_name field required"}), 400

    c = get_db_connection()
    cursor = c.cursor(dictionary=True)


    cursor.execute("SELECT * FROM KEYWORD WHERE keyword_id = %s", (id,))
    keyword = cursor.fetchone()

    if not keyword:
        cursor.close()
        c.close()
        return jsonify({"error": "Keyword not found"}), 404


    try:
        cursor.execute("UPDATE KEYWORD SET keyword_name = %s WHERE keyword_id = %s", (new_name, id))
        c.commit()
        return jsonify({"message": "KEYWORD updated successfully"}), 200
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Error while updating keyword"}), 409
    finally:
        cursor.close()
        c.close()















































if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)

