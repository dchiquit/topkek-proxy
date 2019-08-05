
import requests
from flask import Blueprint, current_app, request, Response, session


def _proxy(new_url, token=None):
    new_url = request.url.replace(request.host_url, new_url + "/")
    print("Proxying", request.url, "to", new_url)
    resp = requests.request(
        method=request.method,
        url=new_url,
        headers={key: value for (key, value)
                 in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding',
                        'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    if token and not filter(lambda h: h[0] == 'Authorization', headers):
        headers += [("Authorization", "JWT " + token)]

    response = Response(resp.content, resp.status_code, headers)
    return response


static_bp = Blueprint("static_routes", __name__, url_prefix="/")


@static_bp.route('/login')
@static_bp.route('/login/')
@static_bp.route('/login/<path:path>')
@static_bp.route('/app')
@static_bp.route('/app/')
@static_bp.route('/app/<path:path>')
@static_bp.route('/admin')
@static_bp.route('/admin/')
@static_bp.route('/admin/<path:path>')
def frontend(path=None):
    print("current session: ", session)
    return _proxy(current_app.config.get('TOPKEK_FRONTEND_URL'))


api_bp = Blueprint("api_routes", __name__, url_prefix="/")


@api_bp.route('/api/login/auth', methods=('POST',))
def api_login_auth():
    response = _proxy(current_app.config.get('TOPKEK_SERVER_URL'))
    print(response)
    print(response.get_json())
    if response.status_code == 200:
        print("yee yee")
        session['access_token'] = response.get_json()['access_token']
    return response


@api_bp.route('/api/login/<path:path>', methods=('GET', 'POST'))
def api_login(path):
    return _proxy(current_app.config.get('TOPKEK_SERVER_URL'))


@api_bp.route('/api/app/<path:path>', methods=('GET', 'POST'))
def api_app(path):
    if 'access_token' in session:
        return _proxy(current_app.config.get('TOPKEK_SERVER_URL'), session['access_token'])
    else:
        return _proxy(current_app.config.get('TOPKEK_SERVER_URL'))


@api_bp.route('/api/admin/<path:path>', methods=('GET', 'POST'))
def api_admin(path):
    if 'access_token' in session:
        return _proxy(current_app.config.get('TOPKEK_SERVER_URL'), session['access_token'])
    else:
        return _proxy(current_app.config.get('TOPKEK_SERVER_URL'))


def init_app(app):
    app.register_blueprint(static_bp)
    app.register_blueprint(api_bp)
