from flask import Blueprint, request
from flask.json import jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended.view_decorators import jwt_required
from werkzeug.exceptions import abort
from . import db

# creating a admin blueprint instance
admin = Blueprint('admin', __name__)

# login route
@admin.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify(msg="Missing JSON in request"), 500
    
    login_id = request.json.get('login_id', None)
    password = request.json.get('password', None)
    
    if not login_id:
        return jsonify(message="Please! enter login_id")
    if not password:
        return jsonify(message="Please enter login password")
    
    if login_id != "admin":
        return jsonify({
            "msg": "login_id is incorrect"
        })
        
    if password != "admin":
        return jsonify({
            "msg": "password is incorrect"
        })
        
    access_token = create_access_token(identity=login_id)
    return jsonify(access_token=access_token)
    
    
# =============================================================================

# Route to get all the tasks
@admin.route("/all-tasks", methods=['GET'])
@jwt_required()
def all_tasks():
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM task")
    
    tasks = []
    
    for task in cursor:
        tasks.append({
            "task_id": task[0],
            "task_assigned": task[1],
            "user_id":  task[2],
            "manager_id": task[3]
        })
        
    return jsonify(tasks), 200
   
   
#    ==================================================================================
   
    
# Delete task route
@admin.route('/delete-task', methods=['POST'])
@jwt_required()
def delete_task():
    if not request.json:
        abort(500)
        
    task_id = request.json.get('task_id')
    
    cursor = db.cursor()
    
    cursor.execute(f"SELECT * FROM task WHERE id = {task_id}")
    
    for task in cursor:
        if not task:
            return jsonify({
                "msg": "task doesn't exists"
            })
        
    cursor.execute(f"DELETE FROM task WHERE id = {task_id}")
    db.commit()
    
    return jsonify({
        "msg": "task deleted"
    }), 200
            
            
            
# ========================================================================

@admin.route('/assign-manager', methods=['POST'])
@jwt_required()
def assign_manager():
    if not request.json:
        abort(500)
        
    # Getting the manager id and user id
    manager_id = request.json.get('manager_id')
    user_id = request.json.get('user_id')
    
    if not manager_id:
        abort(500)
    if not user_id:
        abort(500)
        
    cursor = db.cursor()
    
    # Check if the manager exists
    cursor.execute(f"SELECT * FROM manager WHERE id = {manager_id}")
    if not cursor.fetchone():
        return jsonify({
            "msg": f"No manager found with id: {manager_id}"
        })
    
    # Check if the user exists
    cursor.execute(f"SELECT * FROM user WHERE id = {user_id}")
    if not cursor.fetchone():
        return jsonify({
            "msg": f"No user found with id: {user_id}"
        })
        
    # check if the manager is already assigned to the user
    cursor.execute(f"SELECT * FROM assign_manager WHERE user_id = {user_id}")
    if cursor.fetchone():
        return jsonify({
            "msg": "manager is already assigned to this user"
        })
    
    # Assign the manager to the user
    cursor.execute("INSERT INTO assign_manager (manager_id, user_id) VALUES (%s, %s)", (manager_id, user_id))
    db.commit()
    
    return jsonify({
        "msg": f"mananager_with_id: {manager_id} assigned to user_with_id: {user_id}"
    })
    
    
# ============================================================================================

# unassign manager route
@admin.route('/unassign-manager', methods=['DELETE'])
@jwt_required()
def unassign_manager():
    if not request.json:
        abort(500)
        
    user_id = request.json.get('user_id')
    
    cursor = db.cursor()
    
    # Check if there is any manager
    cursor.execute(f"SELECT * FROM user WHERE id = {user_id}")
    if not cursor.fetchone():
        return jsonify({
            "msg": "user doesn't exists"
        })
    
    # Check if there is any manager to unassign from a particular user
    cursor.execute(f"SELECT * FROM assign_manager WHERE user_id = {user_id}")
    if not cursor.fetchone():
        return jsonify({
            "msg": "No manager to unassign from the user."
        })
    
    cursor.execute(f"DELETE FROM assign_manager WHERE user_id = {user_id}")
    db.commit()
    
    return jsonify({
        "msg": "manager unassigned"
    })