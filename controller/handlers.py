#! /usr/bin/python
# -*- coding:utf-8 -*-

import tornado.web
import os
import sys
import md5
import tornado.gen
import redis
import time

sys.path.append('../')
os.path.join(os.path.dirname(__file__),'../view')

redis_client = redis.StrictRedis("127.0.0.1",6379,0,"xujun123",2000)

def GetFile(dir):
	list_dirs = os.walk(dir) 
	file_list = []
	for root,path,files in list_dirs: 
		for f in files: 
			file_list.append({"name":unicode(f,'utf8'),"size":"%s kb" % os.stat("files/%s"%f).st_size})
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
	@tornado.web.asynchronous
	def get(self):
		cookie = self.get_current_user()
		if cookie:
			f = open("test.html",'r+')
			f2 = open("tempfile.txt","a+")
			content = f.readline()
			greeting = self.get_argument('t')
			f2.write("%s\r\n"%(greeting))
			f.close()
			f2.close()
			self.write(greeting + '%s,user:%s, ip:%s'%(content, cookie, self.request.remote_ip))
			self.finish()
		else:
			self.write("please login")
			self.set_my_cookie(str(self.request.remote_ip))
			self.finish()

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
			redis_client.sadd("file_author:%s"%self.get_current_user(),"file:%s"%filename)
			redis_client.hset("file:%s"%filename,"upload_date:","%s"%time.mktime(time.localtime()))
			redis_client.hset("file:%s"%filename,"md5:","%s"%md5_str)
			self.write("filename:%s finish uploade md5:%s"%(filename, md5_str))

class GetFileListHandler(BaseClass):
	def get(self):
		if not self.get_current_user():
			self.write("please_login")
			self.set_my_cookie(str(self.request.remote_ip))
		else:
			files = GetFile("files")
			self.render("../view/filelist.html", file_list = files)

class DeleteFileHandler(BaseClass):
	def get(self):
		if not self.get_current_user():
			self.write("please_login")
			self.set_my_cookie(str(self.request.remote_ip))
		else:
			filename = self.get_argument("id")
			if FileExist(filename):
				os.remove("files/%s"%filename)
				files = GetFile("files")
				self.render("../view/filelist.html", file_list = files)
