from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from fhirclient import client


db = SQLAlchemy()
DB_NAME = "appdata.db"

settings = {
    'app_id': 'webapp',
    'api_base': 'http://hapi.fhir.org/baseR4'
}
smart = client.FHIRClient(settings=settings)

    
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User, Role, Pro
    
    with app.app_context():
        db.create_all()
        
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id)) # get by primary key
    
    return app