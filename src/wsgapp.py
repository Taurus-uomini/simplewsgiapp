import traceback
import os
from ConfigParser import ConfigParser
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound, MethodNotAllowed
from werkzeug.local import LocalStack, LocalProxy


class wsgiApp:
    __config = None

    def __init__(self):
        self.__url_map = Map([
            Rule('/', endpoint='hello')
            # Rule('/<short_id>', endpoint='follow_short_link'),
            # Rule('/<short_id>+', endpoint='short_link_details')
        ])
        self.is_run = False
        self.__view_functions = dict()
        self.__localstack = LocalStack()
        self.__read_config()

    def __read_config(self):
        if self.__config is None:
            configp = ConfigParser(allow_no_value=True)
            dirlist = os.listdir(os.getcwd() + '\\config')
            config_files = list()
            for dirname in dirlist:
                if dirname.endswith('.ini'):
                    config_files.append(dirname)
            self.__config = dict()
            for config_file in config_files:
                configp.read(os.getcwd() + '\\config\\' + config_file)
                sections = configp.sections()
                for section in sections:
                    item = dict()
                    for key, value in configp.items(section):
                        item[key] = value
                    self.__config[section] = item

    def get_config(self):
        if self.__config is None:
            self.__read_config()
        return self.__config

    def run(self):
        if self.is_run is True:
            print 'the app is already running'
        else:
            config = self.get_config()
            run_simple(
                hostname=config['BaseConfig']['hostname'],
                port=int(config['BaseConfig']['port']),
                application=self
            )
            self.is_run = True

    def get_data(self, request):
        if request.method.lower() == 'post':
            data = request.form.to_dict()
        else:
            data = request.args.to_dict()
        return data

    def get_local_attr(self, attr):
        local_attr = LocalProxy(self.__localstack.top[attr])
        return local_attr

    def get_request(self):
        return self.get_local_attr('request')

    def __push_local_attr(self, local_attr):
        def get_it():
            return local_attr
        return get_it

    def __call__(self, environ, start_response):
        request = Request(environ)
        self.__localstack.push({"request": self.__push_local_attr(request)})
        adapter = self.__url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            status = 200
            if endpoint in self.__view_functions:
                res = self.__view_functions[endpoint]()
            else:
                res = getattr(self, 'on_' + endpoint)(request)
        except NotFound, e:
            status = 404
            res = e.get_body()
        except MethodNotAllowed, e:
            status = 405
            res = e.get_body()
        except HTTPException, e:
            status = 500
            res = e.get_body()
        except Exception, e:
            status = 500
            config = self.get_config()
            if config['BaseConfig']['debug'] == 'true':
                res = traceback.format_exc()
            else:
                print traceback.format_exc()
                res = 'server error'
        finally:
            self.__localstack.pop()
            response = Response(res, status=status, mimetype='text/html')
            return response(environ, start_response)

    def __add_url_rule(self, route, endpoint, f, **options):
        if endpoint is None:
            endpoint = f.__name__
        methods = options.pop('methods', None)
        if methods is not None:
            methods = set(item.upper() for item in methods)
        route = Rule(route, endpoint=endpoint, methods=methods)
        self.__url_map.add(route)
        self.__view_functions[endpoint] = f

    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.__add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def on_hello(self, request):
        data = self.get_data(request)
        return 'hello ' + data['name']
