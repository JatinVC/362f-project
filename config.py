DUBUG=True

# define application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database setup
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}