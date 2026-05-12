from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, BooleanField, FileField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class BookForm(FlaskForm):
    code = StringField('Kode Buku', validators=[DataRequired(), Length(max=64)])
    title = StringField('Judul', validators=[DataRequired(), Length(max=200)])
    author = StringField('Penulis', validators=[DataRequired(), Length(max=120)])
    publisher = StringField('Penerbit', validators=[DataRequired(), Length(max=120)])
    category = StringField('Kategori', validators=[DataRequired(), Length(max=120)])
    year = IntegerField('Tahun Terbit', validators=[Optional(), NumberRange(min=1000, max=2100)])
    isbn = StringField('ISBN', validators=[Optional(), Length(max=32)])
    stock_total = IntegerField('Stok Total', validators=[DataRequired(), NumberRange(min=0)])
    stock_available = IntegerField('Stok Tersedia', validators=[DataRequired(), NumberRange(min=0)])
    shelf_location = StringField('Lokasi Rak', validators=[Optional(), Length(max=80)])
    cover_file = FileField('Upload Cover Buku')
    ebook_file = FileField('Upload File Buku (PDF/EPUB)')
    cover_url = StringField('Cover URL (opsional, fallback)', validators=[Optional(), Length(max=255)])
    status = SelectField('Status', choices=[('available', 'Available'), ('low_stock', 'Low Stock'), ('inactive', 'Inactive')], validators=[DataRequired()])
    description = TextAreaField('Deskripsi', validators=[Optional(), Length(max=2000)])

class AdminForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    full_name = StringField('Nama Lengkap', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password Baru', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[Optional(), EqualTo('password')])
    avatar_url = StringField('Avatar URL', validators=[Optional(), Length(max=255)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    is_active_account = BooleanField('Aktif')

class ProfileForm(FlaskForm):
    full_name = StringField('Nama Lengkap', validators=[DataRequired(), Length(max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    avatar_url = StringField('Avatar URL', validators=[Optional(), Length(max=255)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    password = PasswordField('Password Baru', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[Optional(), EqualTo('password')])
