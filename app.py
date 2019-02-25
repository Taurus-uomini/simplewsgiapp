from src.wsgapp import wsgiApp
from werkzeug.serving import run_simple

app = wsgiApp()


@app.route('/home', methods=['get', 'post'])
@app.route('/home+', methods=['get', 'post'])
def home():
    request = app.get_request()
    data = app.get_data(request)
    return 'home ' + data['name']


@app.route('/test')
def futest():
    return 'test'


if __name__ == '__main__':
    run_simple('localhost', 5000, app)
