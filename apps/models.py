# -*- encoding: utf-8 -*-
from datetime import datetime
from apps import db, login_manager
from flask_login import UserMixin
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from apps.authentication.util import hash_pass

class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin')
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, **kwargs):
        password = kwargs.pop('password', None)
        for key, value in kwargs.items():
            setattr(self, key, value)
        if password is not None:
            self.password = hash_pass(password) if isinstance(password, str) else password

    def set_password(self, password: str):
        self.password = hash_pass(password)

    def check_password(self, password: str) -> bool:
        from apps.authentication.util import verify_pass
        return verify_pass(password, self.password)

    def __repr__(self):
        return f'<Users {self.username}>'

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            raise IntegrityError(str(e), 422)

    def delete_from_db(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            raise IntegrityError(str(e), 422)

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    publisher = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    isbn = db.Column(db.String(32), nullable=True)
    stock_total = db.Column(db.Integer, default=1, nullable=False)
    stock_available = db.Column(db.Integer, default=1, nullable=False)
    shelf_location = db.Column(db.String(80), nullable=True)
    cover_url = db.Column(db.String(255), nullable=True)
    cover_filename = db.Column(db.String(255), nullable=True)
    ebook_filename = db.Column(db.String(255), nullable=True)
    ebook_original_name = db.Column(db.String(255), nullable=True)
    ebook_mime_type = db.Column(db.String(120), nullable=True)
    ebook_size = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(30), default='available', nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

    @property
    def cover_src(self):
        if self.cover_filename:
            return f'assets/img/books/covers/{self.cover_filename}'
        if self.cover_url:
            return self.cover_url
        return None

    @property
    def has_cover(self):
        return bool(self.cover_src)

    @property
    def has_ebook(self):
        return bool(self.ebook_filename)

    @property
    def ebook_display_name(self):
        return self.ebook_original_name or self.ebook_filename or 'File belum diupload'

    @classmethod
    def get_list(cls):
        return cls.query.order_by(cls.created_at.desc()).all()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            raise IntegrityError(str(e), 422)

    def delete_from_db(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            raise IntegrityError(str(e), 422)

@login_manager.user_loader
def user_loader(user_id):
    return Users.query.filter_by(id=user_id).first()
