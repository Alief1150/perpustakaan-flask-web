# -*- encoding: utf-8 -*-
from apps import login_manager
from apps.models import Users

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    return Users.query.filter_by(username=username).first() if username else None
