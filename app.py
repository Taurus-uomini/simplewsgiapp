from src.wsgapp import wsgiApp

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
    app.run()
