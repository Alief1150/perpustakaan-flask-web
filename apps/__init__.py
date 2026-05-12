# -*- encoding: utf-8 -*-
import os
from importlib import import_module
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'authentication_blueprint.login'
login_manager.login_message_category = 'warning'

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module(f'apps.{module_name}.routes')
        app.register_blueprint(module.blueprint)

def create_app(config):
    static_prefix = '/static'
    templates_dir = os.path.dirname(config.BASE_DIR)
    templates_folder = os.path.join(templates_dir, 'templates')
    static_folder = os.path.join(templates_dir, 'static')

    app = Flask(__name__, static_url_path=static_prefix, template_folder=templates_folder, static_folder=static_folder)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    return app
