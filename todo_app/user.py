from flask import Blueprint, request, abort
from flask.json import jsonify
from . import db
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_current_user
from . import jwt

user = Blueprint('user', __name__)

# User account registration route
@user.route('/register', methods=['POST'])
def register():
    if not request.json:
        abort(500)
        
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    name = request.json.get("name", None)
    
    if username is None or password is None or name is None:
        abort(500)
        
    cursor = db.cursor()
    
    cursor.execute(f"SELECT * FROM user WHERE username = '{username}'")
    
    for x in cursor:
        if x:
            return jsonify({
                "message": "username already taken!"
            })
    
    hashed_password = pbkdf2_sha256.hash(password)
    
    cursor.execute("INSERT INTO user (username, name, password) VALUES (%s, %s, %s)", (username, name, hashed_password))
    db.commit()
            
    return jsonify({
        "message": "user account created"
    })
    
    
# ===========================================================================================

@user.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify(msg="Missing JSON in request"), 500
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify(msg="Missing username parameter"), 500
    if not password:
        return jsonify(msg="Missing password parameter"), 500
    
    cursor = db.cursor()
    
    # Fetching the password from the database
    cursor.execute(f"SELECT password FROM user WHERE username = '{username}'")
    
    for pwd in cursor:
        if not pbkdf2_sha256.verify(password, pwd[0]):
            return jsonify("password failed!"), 400
            
            
    # Generating token 
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token, message="Logged in!"), 200 


# ===========================================================================================


# callback to get the manager id from the access token
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    # Get the identity assigned at the time of generating token
    identity = jwt_data["sub"]
    # Get the data of manager based on the identity
    cursor = db.cursor()
    cursor.execute(f"SELECT id FROM user WHERE username = '{identity}'")
    user_id = None
    for id in cursor:
        user_id = id[0]
    return jsonify({
        "id": user_id
    })


@user.route('/all-assigned-tasks')
@jwt_required()
def all_assigned_tasks():
    current_user_id = get_current_user().json.get('id')
    print(current_user_id)
    cursor = db.cursor()
    
    # Getting the all tasks assigned by manager to the users
    cursor.execute(f"SELECT task.id, task.task_assigned, task.user_id, manager.name FROM task RIGHT JOIN manager ON task.manager_id = manager.id WHERE task.user_id = {current_user_id}; ")
    
    if not cursor.fetchone():
        return jsonify({
            "msg": "No task to show"
        })

    tasks = []
    for task in cursor:
        tasks.append({
            "task id": task[0],
            "task_assigned": task[1],
            "user_id": task[2],
            "task_assigned_by": task[3]
        })
    return jsonify(tasks), 200