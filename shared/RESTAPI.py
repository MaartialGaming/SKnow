import cherrypy
import os

class RESTAPI():
    def __init__(self, uri, address, port, GET = None, PUT = None, POST = None, DELETE = None):
        self.uri = uri
        self.address = address
        self.port = port
        self.GET = GET
        self.PUT = PUT
        self.POST = POST
        self.DELETE = DELETE

    exposed = True
    
    def GET(self, *uri, **params):
        if self.GET is not None:
            self.GET
    
    def PUT(self, *uri, **params):
        if self.PUT is not None:
            self.PUT
    
    def POST(self, *uri, **params):
        if self.POST is not None:
            self.POST
    
    def DELETE(self, *uri, **params):
        if self.DELETE is not None:
            self.DELETE

    def start(self):
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True,
            }
        }
        cherrypy.tree.mount(self, f'/{self.uri}', conf)
        cherrypy.config.update({'server.socket_host': self.address})
        cherrypy.config.update({'server.socket_port': self.port})
        cherrypy.engine.start()
    
    def block(self):
        cherrypy.engine.block()
    
    def stop(self):
        cherrypy.engine.exit()

class RESTAPI_webpage(RESTAPI):
    def start(self):
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
				'tools.staticdir.root': os.path.abspath(os.getcwd()),
            },
            '/css':{
                'tools.staticdir.on': True,
                'tools.staticdir.dir':'css'
            },
            '/js':{
                'tools.staticdir.on': True,
                'tools.staticdir.dir':'js'
            },
            '/images':{
                'tools.staticdir.on': True,
                'tools.staticdir.dir':'images'
            },
            '/fonts':{
                'tools.staticdir.on': True,
                'tools.staticdir.dir':'fonts'
            }
        }
        cherrypy.tree.mount(self, f'/{self.uri}', conf)
        cherrypy.config.update({'server.socket_host': self.address})
        cherrypy.config.update({'server.socket_port': self.port})
        cherrypy.engine.start()