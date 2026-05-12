from pathlib import Path
from uuid import uuid4

from flask import render_template, request, redirect, url_for, flash, abort, send_from_directory, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename

from apps.home import blueprint
from apps import db
from apps.forms import BookForm, AdminForm, ProfileForm
from apps.models import Book, Users

ALLOWED_COVER_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_BOOK_EXTENSIONS = {'pdf', 'epub'}


def _sync_stock(book):
    if book.stock_available is None:
        book.stock_available = 0
    if book.stock_total is None:
        book.stock_total = 0
    if book.stock_available > book.stock_total:
        book.stock_available = book.stock_total
    if book.stock_total < 0:
        book.stock_total = 0
    if book.stock_available < 0:
        book.stock_available = 0


def _allowed_extension(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def _save_upload(file_storage, folder_key, allowed_extensions, prefix):
    if not file_storage or not file_storage.filename:
        return None, None, None, None

    original_name = secure_filename(file_storage.filename)
    if not original_name or not _allowed_extension(original_name, allowed_extensions):
        raise ValueError('Format file tidak didukung.')

    suffix = Path(original_name).suffix.lower()
    stored_name = f'{prefix}-{uuid4().hex}{suffix}'
    target_dir = Path(current_app.config[folder_key])
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / stored_name
    file_storage.save(target_path)

    return stored_name, original_name, file_storage.mimetype, target_path.stat().st_size


def _remove_upload(folder_key, filename):
    if not filename:
        return
    file_path = Path(current_app.config[folder_key]) / filename
    if file_path.exists():
        file_path.unlink()


@blueprint.route('/')
@login_required
def index():
    total_books = Book.query.count()
    total_admins = Users.query.count()
    total_available = db.session.query(func.coalesce(func.sum(Book.stock_available), 0)).scalar() or 0
    total_stock = db.session.query(func.coalesce(func.sum(Book.stock_total), 0)).scalar() or 0
    books_by_category = db.session.query(Book.category, func.count(Book.id)).group_by(Book.category).all()
    category_labels = [row[0] for row in books_by_category]
    category_values = [int(row[1]) for row in books_by_category]
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(5).all()
    low_stock_books = Book.query.filter(Book.stock_available <= 3).order_by(Book.stock_available.asc()).limit(5).all()
    return render_template(
        'pages/index.html',
        segment='dashboard',
        total_books=total_books,
        total_admins=total_admins,
        total_available=total_available,
        total_stock=total_stock,
        category_labels=category_labels,
        category_values=category_values,
        recent_books=recent_books,
        low_stock_books=low_stock_books,
    )


@blueprint.route('/books')
@login_required
def books():
    return render_template('pages/books.html', segment='books', books=Book.get_list())


@blueprint.route('/books/<int:book_id>')
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('pages/book_detail.html', segment='books', book=book)


@blueprint.route('/books/<int:book_id>/download')
@login_required
def book_download(book_id):
    book = Book.query.get_or_404(book_id)
    if not book.ebook_filename:
        flash('File buku belum diupload.', 'warning')
        return redirect(url_for('home_blueprint.book_detail', book_id=book.id))

    file_path = Path(current_app.config['BOOK_FILES_DIR']) / book.ebook_filename
    if not file_path.exists():
        flash('File buku tidak ditemukan di server.', 'danger')
        return redirect(url_for('home_blueprint.book_detail', book_id=book.id))

    return send_from_directory(
        current_app.config['BOOK_FILES_DIR'],
        book.ebook_filename,
        as_attachment=True,
        download_name=book.ebook_original_name or book.ebook_filename,
    )


@blueprint.route('/books/new', methods=['GET', 'POST'])
@login_required
def book_new():
    form = BookForm()
    if form.validate_on_submit():
        cover_file = request.files.get('cover_file')
        ebook_file = request.files.get('ebook_file')
        try:
            cover_filename, _, _, _ = _save_upload(cover_file, 'BOOK_COVERS_DIR', ALLOWED_COVER_EXTENSIONS, form.code.data)
            ebook_filename, ebook_original_name, ebook_mime_type, ebook_size = _save_upload(ebook_file, 'BOOK_FILES_DIR', ALLOWED_BOOK_EXTENSIONS, form.code.data)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return render_template('pages/book_form.html', segment='books', form=form, mode='create')

        book = Book(
            code=form.code.data,
            title=form.title.data,
            author=form.author.data,
            publisher=form.publisher.data,
            category=form.category.data,
            year=form.year.data,
            isbn=form.isbn.data,
            stock_total=form.stock_total.data,
            stock_available=form.stock_available.data,
            shelf_location=form.shelf_location.data,
            cover_url=form.cover_url.data,
            cover_filename=cover_filename,
            ebook_filename=ebook_filename,
            ebook_original_name=ebook_original_name,
            ebook_mime_type=ebook_mime_type,
            ebook_size=ebook_size,
            status=form.status.data,
            description=form.description.data,
        )
        _sync_stock(book)
        book.save()
        flash('Buku berhasil ditambahkan.', 'success')
        return redirect(url_for('home_blueprint.books'))
    return render_template('pages/book_form.html', segment='books', form=form, mode='create')


@blueprint.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def book_edit(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        old_cover = book.cover_filename
        old_ebook = book.ebook_filename
        cover_file = request.files.get('cover_file')
        ebook_file = request.files.get('ebook_file')

        try:
            if cover_file and cover_file.filename:
                cover_filename, _, _, _ = _save_upload(cover_file, 'BOOK_COVERS_DIR', ALLOWED_COVER_EXTENSIONS, form.code.data)
                book.cover_filename = cover_filename

            if ebook_file and ebook_file.filename:
                ebook_filename, ebook_original_name, ebook_mime_type, ebook_size = _save_upload(ebook_file, 'BOOK_FILES_DIR', ALLOWED_BOOK_EXTENSIONS, form.code.data)
                book.ebook_filename = ebook_filename
                book.ebook_original_name = ebook_original_name
                book.ebook_mime_type = ebook_mime_type
                book.ebook_size = ebook_size

            form.populate_obj(book)
            book.cover_filename = book.cover_filename or old_cover
            book.ebook_filename = book.ebook_filename or old_ebook
            _sync_stock(book)
            book.save()

            if cover_file and cover_file.filename and old_cover and old_cover != book.cover_filename:
                _remove_upload('BOOK_COVERS_DIR', old_cover)
            if ebook_file and ebook_file.filename and old_ebook and old_ebook != book.ebook_filename:
                _remove_upload('BOOK_FILES_DIR', old_ebook)

            flash('Buku berhasil diperbarui.', 'success')
            return redirect(url_for('home_blueprint.books'))
        except ValueError as exc:
            flash(str(exc), 'danger')
            return render_template('pages/book_form.html', segment='books', form=form, mode='edit', book=book)
    return render_template('pages/book_form.html', segment='books', form=form, mode='edit', book=book)


@blueprint.route('/books/<int:book_id>/delete', methods=['POST'])
@login_required
def book_delete(book_id):
    book = Book.query.get_or_404(book_id)
    _remove_upload('BOOK_COVERS_DIR', book.cover_filename)
    _remove_upload('BOOK_FILES_DIR', book.ebook_filename)
    book.delete_from_db()
    flash('Buku berhasil dihapus.', 'warning')
    return redirect(url_for('home_blueprint.books'))


@blueprint.route('/admins')
@login_required
def admins():
    users = Users.query.order_by(Users.created_at.desc()).all()
    return render_template('pages/admins.html', segment='admins', users=users)


@blueprint.route('/admins/new', methods=['GET', 'POST'])
@login_required
def admin_new():
    form = AdminForm()
    if form.validate_on_submit():
        if Users.query.filter((Users.username == form.username.data) | (Users.email == form.email.data)).first():
            flash('Username atau email sudah dipakai.', 'danger')
        else:
            user = Users(
                username=form.username.data,
                full_name=form.full_name.data,
                email=form.email.data,
                avatar_url=form.avatar_url.data,
                bio=form.bio.data,
                is_active_account=bool(form.is_active_account.data),
                role='admin',
                password=form.password.data or 'admin123',
            )
            user.save()
            flash('Admin baru berhasil dibuat.', 'success')
            return redirect(url_for('home_blueprint.admins'))
    return render_template('pages/admin_form.html', segment='admins', form=form, mode='create')


@blueprint.route('/admins/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit(user_id):
    user = Users.query.get_or_404(user_id)
    form = AdminForm(obj=user)
    if request.method == 'GET':
        form.is_active_account.data = user.is_active_account
    if form.validate_on_submit():
        if Users.query.filter(((Users.username == form.username.data) | (Users.email == form.email.data)) & (Users.id != user.id)).first():
            flash('Username atau email sudah dipakai akun lain.', 'danger')
        else:
            user.username = form.username.data
            user.full_name = form.full_name.data
            user.email = form.email.data
            user.avatar_url = form.avatar_url.data
            user.bio = form.bio.data
            user.is_active_account = bool(form.is_active_account.data)
            if form.password.data:
                user.set_password(form.password.data)
            user.role = 'admin'
            user.save()
            flash('Admin berhasil diperbarui.', 'success')
            return redirect(url_for('home_blueprint.admins'))
    return render_template('pages/admin_form.html', segment='admins', form=form, mode='edit', user=user)


@blueprint.route('/admins/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete(user_id):
    if current_user.id == user_id:
        flash('Akun sendiri tidak bisa dihapus.', 'danger')
        return redirect(url_for('home_blueprint.admins'))
    user = Users.query.get_or_404(user_id)
    user.delete_from_db()
    flash('Admin berhasil dihapus.', 'warning')
    return redirect(url_for('home_blueprint.admins'))


@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.avatar_url = form.avatar_url.data
        current_user.bio = form.bio.data
        if form.password.data:
            current_user.set_password(form.password.data)
        current_user.save()
        flash('Profil berhasil diperbarui.', 'success')
        return redirect(url_for('home_blueprint.profile'))
    return render_template('pages/profile.html', segment='profile', form=form, user=current_user)


@blueprint.app_template_filter('replace_value')
def replace_value(value, args):
    return value.replace(args, ' ').title()
