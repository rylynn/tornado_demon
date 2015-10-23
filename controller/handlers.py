#! /usr/bin/python
# -*- coding:utf-8 -*-

import tornado.web
import os
import sys
import md5
import tornado.gen
import redis
import time
from chathandle import *
sys.path.append('../')

redis_client = redis.StrictRedis("127.0.0.1",6379,0,"xujun123",2000)

def GetFile(dir, current_user):
	list_dirs = os.walk(dir) 
	file_list = []
	for root,path,files in list_dirs: 
		for f in files: 
			file_info =  redis_client.hgetall("file:%s"%f)
			md5_str = file_info["md5:"]
			update_time = file_info["upload_date:"]
			author_str = file_info["author:"]
			can_delete = (current_user == author_str)
			file_list.append({"name":unicode(f,'utf8'),"size":"%skb" % os.stat("files/%s"%f).st_size, "update_time":update_time, "md5":md5_str,"author":author_str,"can_delete":can_delete})
	return file_list

def FileExist(file):
	dir_path = "files"
	list_dirs = os.walk(dir_path)
	for root,path,files in list_dirs:
		for f in files:
			if file == f:
				return True
	return False

def MakeMd5(data):
	return md5.new(data).hexdigest()

class Entry(tornado.web.UIModule):
	def render(self, entry, show_comments=False):
		return self.render_string(
				"module-entry.html", show_comments=show_comments)

class BaseClass(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("user")
	def set_my_cookie(self, key):
		self.set_secure_cookie("user",key)

class IndexHandler(BaseClass):
	def get(self):
		self.render("../view/chat_page.html", messages=ChatSocketHandler.cache)
class UpdateFileHandler(BaseClass):
	def get(self):
		if not self.get_current_user():
			self.write("please login")
		else:
			self.render("../view/upload.html")

	def post(self):
		upload_path=os.path.join(os.path.dirname(__file__),'../files')
		file_metas=self.request.files['file']
		for meta in file_metas:
			filename=meta['filename']
		filepath=os.path.join(upload_path,filename)
		if FileExist(file) == True:
			self.write("file exists, if you wanner update, delete it first")
		else:
			with open(filepath,'wb') as up:
				up.write(meta['body'])
			md5_str =  MakeMd5(meta['body'])
			redis_client.hset("file:%s"%filename,"upload_date:","%s"%time.mktime(time.localtime()))
			redis_client.hset("file:%s"%filename,"md5:","%s"%md5_str)
			redis_client.hset("file:%s"%filename,"author:","%s"%self.get_current_user())
			self.write("filename:%s finish uploade md5:%s"%(filename, md5_str))
			self.redirect("/file",permanent=True)

class GetFileListHandler(BaseClass):
	def get(self):
		if not self.get_current_user():
			self.write("please_login")
			self.set_my_cookie(str(self.request.remote_ip))
		else:
			files = GetFile("files", self.get_current_user())
			self.render("../view/filelist.html", file_list = files)

class DeleteFileHandler(BaseClass):
	def get(self):
		if not self.get_current_user():
			self.write("please_login")
			self.set_my_cookie(str(self.request.remote_ip))
		else:
			filename = self.get_argument("id")
			if FileExist(filename):
				author = redis_client.hget("file:%s"%filename,"author:")
				if author and author == self.get_current_user():
					os.remove("files/%s"%filename)
				self.redirect("/file",permanent=True)

class DownLoadFileHandler(BaseClass):
	def get(self):
		file_name = self.get_argument("file_name")
		if FileExist(file_name):
			download_path=os.path.join(os.path.dirname(__file__),'../files',file_name)
			self.set_header ('Content-Type', 'application/octet-stream')
			self.set_header ('Content-Disposition', 'attachment; filename='+file_name)
			with open(download_path,'rb+') as f:
				while True:
					data = f.read(4096)
					if not data:
						break
					self.write(data)
			self.finish()
