import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
	waiters = set()
	cache = []
	cache_size = 200

	def allow_draft76(self):
		return True
	def open(self):
		print("websocket open")
		ChatSocketHandler.waiters.add(self)
	def on_close(self):
		ChatSocketHandler.waiters.remove(self)
	@classmethod
	def update_cache(cls, chat):
		cls.cache.append(chat)
		if len(cls.cache) > cls.cache_size:
			cls.cache = cls.cache[-cls.cache_size:]
	@classmethod
	def send_updates(cls, chat):
		for waiter in cls.waiters:
			try:
				waiter.write_message(chat)
			except:
				print("Error sending message")
	def on_message(self, message):
		print("get message:%s"%message)
		ChatSocketHandler.send_updates(message)
