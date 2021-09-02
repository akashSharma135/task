from flask import Flask
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Akash135#",
    database="todoDB"
)

jwt = None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dd3ff1e5d693dda7482aa5f6e982da03'
    
    from flask_jwt_extended import JWTManager
    global jwt
    jwt = JWTManager(app)
    
    from .manager import manager
    from .user import user
    from .admin import admin
    
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(manager, url_prefix='/manager')
    app.register_blueprint(admin, url_prefix='/admin')
    
    return app