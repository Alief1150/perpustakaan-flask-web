from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_user, logout_user
from apps.authentication import blueprint
from apps.forms import LoginForm
from apps.models import Users

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.index'))

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Users.query.filter((Users.username == form.username.data) | (Users.email == form.username.data)).first()
        if not user:
            flash('Akun tidak ditemukan.', 'danger')
        elif not user.is_active_account:
            flash('Akun admin nonaktif.', 'danger')
        elif not user.check_password(form.password.data):
            flash('Username/email atau password salah.', 'danger')
        else:
            login_user(user)
            flash('Login berhasil.', 'success')
            return redirect(url_for('home_blueprint.index'))

    return render_template('authentication/login.html', form=form, segment='login')

@blueprint.route('/logout')
def logout():
    logout_user()
    flash('Berhasil logout.', 'info')
    return redirect(url_for('authentication_blueprint.login'))
