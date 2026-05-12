# -*- encoding: utf-8 -*-
import os
from sys import exit
from pathlib import Path
from sqlalchemy import inspect, text
from flask_migrate import Migrate
from apps.config import config_dict
from apps import create_app, db
from apps.models import Users, Book

DEBUG = (os.getenv('DEBUG', 'False') == 'True')
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)

def ensure_upload_dirs():
    for folder in (app.config['BOOK_COVERS_DIR'], app.config['BOOK_FILES_DIR']):
        Path(folder).mkdir(parents=True, exist_ok=True)

def ensure_book_schema():
    inspector = inspect(db.engine)
    if 'books' not in inspector.get_table_names():
        return

    existing_columns = {column['name'] for column in inspector.get_columns('books')}
    migrations = {
        'cover_filename': 'ALTER TABLE books ADD COLUMN cover_filename VARCHAR(255)',
        'ebook_filename': 'ALTER TABLE books ADD COLUMN ebook_filename VARCHAR(255)',
        'ebook_original_name': 'ALTER TABLE books ADD COLUMN ebook_original_name VARCHAR(255)',
        'ebook_mime_type': 'ALTER TABLE books ADD COLUMN ebook_mime_type VARCHAR(120)',
        'ebook_size': 'ALTER TABLE books ADD COLUMN ebook_size INTEGER',
    }
    for column_name, ddl in migrations.items():
        if column_name not in existing_columns:
            db.session.execute(text(ddl))
    db.session.commit()


def backfill_book_assets():
    default_covers = {
        'BK-001': 'book-flask.jpg',
        'BK-002': 'book-database.jpg',
        'BK-003': 'book-network.jpg',
    }
    for code, filename in default_covers.items():
        book = Book.query.filter_by(code=code).first()
        if book and not book.cover_filename:
            book.cover_filename = filename
            book.save()


def seed_data():
    if Users.query.count() == 0:
        admin = Users(
            username='admin',
            full_name='Administrator',
            email='admin@pnj.local',
            role='admin',
            is_active_account=True,
            avatar_url='https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80',
            bio='Admin utama Perpustakaan PNJ',
            password='admin123',
        )
        admin.save()

    if Book.query.count() == 0:
        samples = [
            Book(code='BK-001', title='Pemrograman Web dengan Flask', author='Tim Dosen', publisher='PNJ Press', category='Pemrograman', year=2024, isbn='978000000001', stock_total=5, stock_available=4, shelf_location='A-01', cover_filename='book-flask.jpg', status='available', description='Buku pengantar Flask untuk pengembangan web.'),
            Book(code='BK-002', title='Basis Data Lanjut', author='Tim Kurikulum', publisher='PNJ Press', category='Basis Data', year=2023, isbn='978000000002', stock_total=3, stock_available=2, shelf_location='B-02', cover_filename='book-database.jpg', status='low_stock', description='Referensi basis data dan desain schema.'),
            Book(code='BK-003', title='Jaringan Komputer Dasar', author='Laboratorium TJKT', publisher='PNJ Press', category='Jaringan', year=2022, isbn='978000000003', stock_total=6, stock_available=6, shelf_location='C-03', cover_filename='book-network.jpg', status='available', description='Dasar-dasar jaringan komputer untuk mahasiswa.'),
        ]
        for book in samples:
            book.save()

with app.app_context():
    ensure_upload_dirs()
    db.create_all()
    ensure_book_schema()
    seed_data()
    backfill_book_assets()

Migrate(app, db)

if DEBUG:
    app.logger.info('DEBUG            = %s', DEBUG)
    app.logger.info('DBMS             = %s', app_config.SQLALCHEMY_DATABASE_URI)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
