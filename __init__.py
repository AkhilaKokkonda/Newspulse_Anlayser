

# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
# from dotenv import load_dotenv

# # Initialize extensions
# db = SQLAlchemy()
# bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = "main.login"  # redirect if not logged in
# login_manager.login_message_category = "info"

# def create_app():
#     load_dotenv()  # Load .env variables

#     app = Flask(__name__)
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///site.db')
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     # Initialize extensions
#     db.init_app(app)
#     bcrypt.init_app(app)
#     login_manager.init_app(app)

#     # Register blueprints
#     from app import routes
#     app.register_blueprint(routes.bp)

#     # Create database tables
#     with app.app_context():
#         db.create_all()

#     return app

# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
# from dotenv import load_dotenv

# # Initialize extensions
# db = SQLAlchemy()
# bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = "main.login"  # redirect if not logged in
# login_manager.login_message_category = "info"

# def create_app():
#     load_dotenv()  # Load .env variables

#     app = Flask(__name__)
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///site.db')
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     # Initialize extensions
#     db.init_app(app)
#     bcrypt.init_app(app)
#     login_manager.init_app(app)

#     # Import and register blueprints
#     from app.routes import bp as main_bp
#     app.register_blueprint(main_bp)

#     # Ensure database tables exist
#     with app.app_context():
#         db.create_all()

#     return app



# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
# from dotenv import load_dotenv

# db = SQLAlchemy()
# bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = "main.login"
# login_manager.login_message_category = "info"

# def create_app():
#     load_dotenv()

#     app = Flask(__name__, instance_relative_config=True)
#     os.makedirs(app.instance_path, exist_ok=True)

#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
#         'SQLALCHEMY_DATABASE_URI',
#         f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"
#     )
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     db.init_app(app)
#     bcrypt.init_app(app)
#     login_manager.init_app(app)

#     from app.routes import bp as main_bp
#     app.register_blueprint(main_bp)

#     with app.app_context():
#         db.create_all()

#     return app




# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
# from dotenv import load_dotenv

# db = SQLAlchemy()
# bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = "routes.login"  # fixed
# login_manager.login_message_category = "info"

# def create_app():
#     load_dotenv()

#     app = Flask(__name__, instance_relative_config=True)
#     os.makedirs(app.instance_path, exist_ok=True)

#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
#         'SQLALCHEMY_DATABASE_URI',
#         f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"
#     )
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     db.init_app(app)
#     bcrypt.init_app(app)
#     login_manager.init_app(app)

#     # Correct Blueprint import
#     from .routes import routes as main_bp
#     app.register_blueprint(main_bp)

#     with app.app_context():
#         db.create_all()

#     return app



# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
# from dotenv import load_dotenv

# db = SQLAlchemy()
# bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = "routes.login"  # Adjust if you have a login route
# login_manager.login_message_category = "info"

# nlp_instance = None  # Will hold NLPAnalyzer instance

# def create_app():
#     global nlp_instance
#     load_dotenv()

#     app = Flask(__name__, instance_relative_config=True)
#     os.makedirs(app.instance_path, exist_ok=True)

#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
#         'SQLALCHEMY_DATABASE_URI',
#         f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"
#     )
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     # Initialize extensions
#     db.init_app(app)
#     bcrypt.init_app(app)
#     login_manager.init_app(app)

#     # Import models here to avoid circular imports
#     from app.models import User
#     from .nlp_utils import NLPAnalyzer

#     # ------------------------------
#     # Flask-Login user loader
#     # ------------------------------
#     @login_manager.user_loader
#     def load_user(user_id):
#         return User.query.get(int(user_id))

#     # ------------------------------
#     # Register Blueprints
#     # ------------------------------
#     from .routes import routes as main_bp
#     app.register_blueprint(main_bp)

#     # ------------------------------
#     # Create DB tables and NLP instance
#     # ------------------------------
#     with app.app_context():
#         db.create_all()
#         nlp_instance = NLPAnalyzer()
#         print("NLPAnalyzer instance created!")

#     return app


# # app/__init__.py
# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
# from dotenv import load_dotenv

# # ------------------------
# # Extensions
# # ------------------------
# db = SQLAlchemy()
# bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = "main.login"  # endpoint for login route
# login_manager.login_message_category = "info"

# # ------------------------
# # App factory
# # ------------------------
# def create_app():
#     load_dotenv()

#     app = Flask(__name__, instance_relative_config=True)
#     os.makedirs(app.instance_path, exist_ok=True)

#     # Config
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
#         'SQLALCHEMY_DATABASE_URI',
#         f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"
#     )
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     # Initialize extensions
#     db.init_app(app)
#     bcrypt.init_app(app)
#     login_manager.init_app(app)

#     # ------------------------
#     # Register blueprints
#     # ------------------------
#     from .routes import bp as main_bp
#     app.register_blueprint(main_bp)

#     # ------------------------
#     # Database creation
#     # ------------------------
#     with app.app_context():
#         db.create_all()

#     return app



# # app/__init__.py
# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
# from dotenv import load_dotenv

# db = SQLAlchemy()
# bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = "main.login"
# login_manager.login_message_category = "info"

# def create_app():
#     load_dotenv()
#     app = Flask(__name__, instance_relative_config=True)
#     os.makedirs(app.instance_path, exist_ok=True)

#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
#         'SQLALCHEMY_DATABASE_URI',
#         f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"
#     )
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     db.init_app(app)
#     bcrypt.init_app(app)
#     login_manager.init_app(app)

#     # Import models here to avoid circular imports
#     from .models import User

#     # ✅ Define user_loader for Flask-Login
#     @login_manager.user_loader
#     def load_user(user_id):
#         return User.query.get(int(user_id))

#     # Register blueprint
#     from .routes import bp as main_bp
#     app.register_blueprint(main_bp)

#     # Create DB tables
#     with app.app_context():
#         db.create_all()

#     return app



import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "info"

def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import models to avoid circular imports
    from .models import User

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprint
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Create DB tables
    with app.app_context():
        db.create_all()

    return app
