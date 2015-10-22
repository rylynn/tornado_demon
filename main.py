#! /usr/bin/python
# -*- coding:utf-8 -*-
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import sys
sys.path.append('./controller')
from handlers import *

os.path.join(os.path.dirname(__file__),'controller')
os.path.join(os.path.dirname(__file__),'view')

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)
settings = { "cookie_secret":"yy_hash_md5",
		"xsrf_cookies": True,
		"autoreload": True,
		"debug": True,
		}

if __name__ == "__main__":
	tornado.options.parse_command_line()
	app = tornado.web.Application(handlers=[(r"/", IndexHandler),(r"/uploadfile", UpdateFileHandler),(r"/file",GetFileListHandler),(r"/delete",DeleteFileHandler)],**settings)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(8080)
	tornado.ioloop.IOLoop.instance().start()
