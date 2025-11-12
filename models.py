"""Database models for the markitdown API application."""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return the user ID as a string (required by Flask-Login)."""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """Return True if user is authenticated."""
        return True
    
    @property
    def is_active(self):
        """Return True if user is active."""
        return True
    
    @property
    def is_anonymous(self):
        """Return False as this is not an anonymous user."""
        return False


class Conversion(Base):
    """Conversion model for storing document conversions."""
    __tablename__ = 'conversions'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_path = Column(String(500), nullable=False)
    markdown_content = Column(Text, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)  # in bytes
    
    def to_dict(self):
        """Convert the conversion to a dictionary."""
        return {
            'id': self.id,
            'filename': self.filename,
            'markdown_content': self.markdown_content,
            'upload_time': self.upload_time.isoformat(),
            'file_size': self.file_size
        }


class AppConfig(Base):
    """Application configuration model."""
    __tablename__ = 'app_config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db(database_url='sqlite:///markitdown.db'):
    """Initialize the database and create tables."""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Create and return a database session."""
    Session = sessionmaker(bind=engine)
    return Session()


def init_default_user(session):
    """Initialize default admin user if not exists."""
    user = session.query(User).filter_by(username='admin').first()
    if not user:
        user = User(username='admin', is_admin=True)
        user.set_password('admin')
        session.add(user)
        session.commit()
    return user


def init_default_config(session):
    """Initialize default application configuration."""
    configs = [
        ('allowed_extensions', '.pdf,.docx,.doc,.txt,.html,.htm,.pptx,.xlsx'),
        ('max_file_size', '10485760'),  # 10MB in bytes
    ]
    
    for key, value in configs:
        config = session.query(AppConfig).filter_by(key=key).first()
        if not config:
            config = AppConfig(key=key, value=value)
            session.add(config)
    
    session.commit()
