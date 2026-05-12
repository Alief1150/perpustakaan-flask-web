# -*- encoding: utf-8 -*-
from pathlib import Path
import os

class Config(object):
    BASE_DIR = Path(__file__).resolve().parent
    SECRET_KEY = os.getenv('SECRET_KEY', 'perpustakaan-pnj-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + str(BASE_DIR / 'perpustakaan_pnj.db')
    )
    BOOK_COVERS_DIR = str(BASE_DIR.parent / 'static' / 'assets' / 'img' / 'books' / 'covers')
    BOOK_FILES_DIR = str(BASE_DIR.parent / 'uploads' / 'books')
    BOOK_DEFAULT_COVER = 'assets/img/books/covers/default-book.jpg'
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8

class ProductionConfig(Config):
    DEBUG = False

class DebugConfig(Config):
    DEBUG = True

config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig,
}
