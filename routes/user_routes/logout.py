from flask import redirect, url_for
from . import user_routes
from DatabaseHandling.authentication import logout_func

@user_routes.route('/logout', methods=['GET'], endpoint="logout")
def logout():
    logout_func()
    return redirect(url_for('user_routes.login'))
