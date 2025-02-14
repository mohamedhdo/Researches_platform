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
@login_required
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
@login_required
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
@login_required
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


################### RESEARCHER CRUD #############################

@app.route('/profile-update',methods=['POST'])
@login_required
def update_researcher():

    user_id=session['user_id']
    data=request.json


    allowed_fields = ['first_name','last_name','email', 'password','university_id','field_id']

    updates = {}
    for field in allowed_fields:
        if field in data:
            updates[field] = data[field]

    if not updates:
        return jsonify({"error": "No valid fields provided"}), 400

    if 'password' in updates:
        updates['password'] = bcrypt.generate_password_hash(updates['password']).decode('utf-8')

    c=get_db_connection()
    cursor=c.cursor()

    set_clause = ", ".join(f"{key} = %s" for key in updates.keys())
    values = tuple(updates.values()) + (str(user_id),)


    try:
        query=f'UPDATE RESEARCHER SET {set_clause} WHERE researcher_id=%s'
        cursor.execute(query,values)
        c.commit()
        cursor.close()
        c.close()
        return jsonify({'message':'Profile updated successfully'})
    except mysql.connector.IntegrityError as e:
        cursor.close()
        c.close()
        return jsonify({"error":"error while inserting data","e":str(e)})


@app.route('/profile-delete',methods=['DELETE'])
@login_required
def delete_researcher():
    user_id=session['user_id']
    data=request.json

    password=data['password']

    if not password:
        return jsonify({"error":"password field required"})

    c=get_db_connection()
    cursor=c.cursor(dictionary=True)

    cursor.execute('SELECT * FROM RESEARCHER WHERE researcher_id=%s',(user_id,))
    user=cursor.fetchone()



    if user and bcrypt.check_password_hash(user['password'], password):
        cursor.execute('DELETE FROM RESEARCHER WHERE researcher_id=%s',(user_id,))
        c.commit()
        session.clear()
        cursor.close()
        c.close()
        return jsonify({"message":"researcher deleted successfully,you have been logged out"})
    cursor.close()
    c.close()
    return jsonify({"error": "Invalid password"}), 401

############### POST CRUD #########################################################

@app.route('/post',methods=['POST'])
@login_required
def create_post():
    data=request.json
    user_id=session['user_id']
    title=data.get('title')
    description=data.get('description')
    content=data.get('content')
    categories=data.get('categories')
    keywords=data.get('keywords')

    if not all([title,description,content,categories,keywords]):
        return jsonify({"error":"all fields are required"})

    c=get_db_connection()
    cursor=c.cursor()
    try:
        cursor.execute('INSERT INTO POST (researcher_id,title,description,content) VALUES (%s,%s,%s,%s)',(user_id,title,description,content,))
        post_id = cursor.lastrowid
        for category in categories:
            cursor.execute('INSERT INTO POST_CATEGORY (post_id,category_id) VALUES (%s,%s)',(post_id,category,))

        for keyword in keywords:
            cursor.execute('INSERT INTO POST_KEYWORDS (post_id,keyword_id) VALUES (%s,%s)', (post_id, keyword,))

        c.commit()
        return {"message":"Post created successfully"}
    except mysql.connector.IntegrityError as e:
        return jsonify({"error":str(e)})
    finally:
        cursor.close()
        c.close()

@app.route('/post/<int:id>',methods=['DELETE'])
@login_required
def delete_post(id):
    user_id=session['user_id']

    c=get_db_connection()
    cursor=c.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM POST WHERE post_id=%s',(id,))
        post=cursor.fetchone()
        user=post['researcher_id']
        if user != user_id:
            return jsonify({"error":"You can only delete posts that you created"})

        cursor.execute('DELETE FROM POST WHERE post_id=%s',(id,))
        c.commit()
        return jsonify({"message":"Post deleted successfully"})
    except mysql.connector.IntegrityError as e:
        return jsonify({"error": str(e)})
    finally:
        cursor.close()
        c.close()

@app.route('/post-update/<int:id>',methods=['POST'])
def update_post(id):
    user_id = session['user_id']
    data=request.json
    c = get_db_connection()
    cursor = c.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM POST WHERE post_id=%s', (id,))
        post = cursor.fetchone()
        user = post['researcher_id']
        if user != user_id:
            return jsonify({"error": "You can only delete posts that you created"})
        title = data.get('title')
        description = data.get('description')
        content = data.get('content')
        categories = data.get('categories')
        keywords = data.get('keywords')

        fields = {
            "title": title,
            "description": description,
            "content": content,
            # "categories": categories,
            # "keywords": keywords
        }


        updated = {key: value for key, value in fields.items() if value is not None}
        set_clause = ", ".join(f"{key} = %s" for key in updated.keys())
        values = tuple(updated.values()) + (id,)

        cursor.execute(f'UPDATE POST SET {set_clause} WHERE post_id=%s',values)
        cursor.execute('DELETE FROM POST_CATEGORY WHERE post_id=%s',(id,))
        cursor.execute('DELETE FROM POST_KEYWORDS WHERE post_id=%s', (id,))
        for category in categories:
            cursor.execute('INSERT INTO POST_CATEGORY (post_id,category_id) VALUES (%s,%s)',(id,category,))

        for keyword in keywords:
            cursor.execute('INSERT INTO POST_KEYWORDS (post_id,keyword_id) VALUES (%s,%s)', (id, keyword,))
        c.commit()
        return jsonify({"message":"Post updated successfully"})
    except mysql.connector.IntegrityError as e:
        return jsonify({"error":str(e)})
    finally:
        cursor.close()
        c.close()


########## LIKE FEATURE##################
@app.route('/like/<int:id>',methods=['POST'])
@login_required
def like_unlike(id):
    user_id=session['user_id']
    c=get_db_connection()
    cursor=c.cursor()
    try:
        cursor.execute('SELECT * FROM POST_LIKE WHERE researcher_id=%s AND post_id=%s',(user_id,id,))
        like=cursor.fetchone()
        if not like:
            cursor.execute('INSERT INTO POST_LIKE (researcher_id,post_id) VALUES (%s,%s)',(user_id,id,))
            c.commit()
            return jsonify({"message":"Liked the post"})
        else:
            cursor.execute('DELETE FROM POST_LIKE WHERE researcher_id=%s AND post_id=%s',(user_id,id,))
            c.commit()
        return jsonify({"message":"Unliked the post"})
    except mysql.connector.IntegrityError as e:
        return jsonify({"error":str(e)})
    finally:
        cursor.close()
        c.close()


@app.route('/comment/<int:id>',methods=['POST'])
def create_comment(id):
    user_id=session['user_id']
    data=request.json
    comment=data['content']

    if not comment:
        return jsonify({"error": " you should provide the content of the comment"})

    c=get_db_connection()
    cursor=c.cursor()
    try:
        cursor.execute('INSERT INTO COMMENT (researcher_id,post_id,content) VALUES (%s,%s,%s)',(user_id,id,comment,))
        c.commit()
        return jsonify({"message":"comment added successfully"})
    except mysql.connector.IntegrityError as e:
        return  jsonify({"error":str(e)})
    finally:
        cursor.close()
        c.close()

@app.route('/comment/<int:id>',methods=['DELETE'])
def delete_comment(id):

    c=get_db_connection()
    cursor=c.cursor(dictionary=True)
    user_id=session['user_id']
    cursor.execute('SELECT * FROM COMMENT WHERE comment_id=%s',(id,))
    comment=cursor.fetchone()
    if not comment:
        return jsonify({"error":"comment does not exist"})
    if user_id!=comment['researcher_id']:
        return jsonify({"error":"You can only delete comments that you created"})
    try:
        cursor.execute('DELETE FROM COMMENT WHERE comment_id=%s',(id,))
        c.commit()
        return jsonify({"message":"Comment deleted successfully"})
    except mysql.connector.IntegrityError as e:
        return jsonify({"error":str(e)})
    finally:
        cursor.close()
        c.close()













































if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)

