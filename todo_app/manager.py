from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from . import db
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token
from . import jwt

# Creating an instance of manager blueprint
manager = Blueprint('manager', __name__)

# signup route
@manager.route('/register', methods=['POST'])
def register():
    if not request.json:
        abort(500)
        
    # getting the details 
    manager_login = request.json.get("manager_login", None)
    password = request.json.get("password", None)
    name = request.json.get("name", None)
    
    # if any field is missing then abort with status 500
    if manager_login is None or password is None or name is None:
        abort(500)
        
    
    cursor = db.cursor()
    # check if the manager_login already exists
    cursor.execute(f"SELECT * FROM manager WHERE manager_login = '{manager_login}'")
    
    for x in cursor:
        if x:
            return jsonify({
                "message": "manager_login already taken!"
            })
    
    hashed_password = pbkdf2_sha256.hash(password)
    
    # Creating the manager account
    cursor.execute("INSERT INTO manager (manager_login, name, password) VALUES (%s, %s, %s)", (manager_login, name, hashed_password))
    db.commit()
            
    return jsonify({
        "message": "user account created"
    })
 
   
# ====================================================================================
 
# login route
@manager.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify(msg="Missing JSON in request"), 500
    
    manager_login = request.json.get('manager_login', None)
    password = request.json.get('password', None)
    if not manager_login:
        return jsonify(msg="Missing manager_login parameter"), 500
    if not password:
        return jsonify(msg="Missing password parameter"), 500
    
    cursor = db.cursor()
    
    cursor.execute(f"SELECT id, password FROM manager WHERE manager_login = '{manager_login}'")
    id = None
    for pwd in cursor:
        id = pwd[0]
        if not pbkdf2_sha256.verify(password, pwd[1]):
            return jsonify("password failed!"), 400
            
    access_token = create_access_token(identity=id)
    return jsonify(access_token=access_token), 200 
    
    
# ======================================================================================================
    

# assign task route
@manager.route('/assign-task/', methods=['POST'])
@jwt_required()
def assign_task():
    if not request.json:
        abort(500)
        
    user_id = request.json.get('user_id')
    task_assigned = request.json.get('task_assigned')
    
    if not user_id:
        return jsonify(msg="Missing user_id parameter"), 500
    if not task_assigned:
        return jsonify(msg="Missing task_assigned parameter"), 500
    
    # get the manager id of logged in manager
    current_manager_id = get_jwt_identity()
    
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM user WHERE id = {user_id}")
    
    if not cursor.fetchone():
        return jsonify({
            "message": "user doesn't exists"
        })
    
    cursor.execute(f"SELECT user_id FROM assign_manager WHERE manager_id = {current_manager_id}")
    
    for id in cursor:
        if id[0] == user_id:
            cursor.execute("INSERT INTO task (task_assigned, user_id, manager_id) VALUES (%s, %s, %s)", (task_assigned, user_id, current_manager_id))
            db.commit()
            return jsonify({
                "msg": f"task assigned to userId: {user_id}"
            })
    
    return jsonify({
        "msg": "You cannot assign task to the user"
    })  
    
    
    
# ====================================================================================


@manager.route('/all-assigned-tasks')
@jwt_required()
def all_assigned_tasks():
    current_manager_id = get_jwt_identity()
    print(current_manager_id)
    cursor = db.cursor()
    
    # Getting the all tasks assigned by manager to the users
    cursor.execute(f"SELECT task.id, task.task_assigned, task.user_id, user.name FROM task RIGHT JOIN user ON task.user_id = user.id WHERE task.manager_id = {current_manager_id}; ")

    tasks = []
    for task in cursor:
        print(task)
        tasks.append({
            "task id": task[0],
            "task_assigned": task[1],
            "user_id": task[2],
            "name of user": task[3]
        })
    return jsonify(tasks), 200
    