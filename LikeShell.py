# -*- coding: utf-8 -*-
import os

class LikeShell:
	def __init__(self, root="/root"):
		self.root = root
	
	def getRoot(self):
		return self.root
		
	def setRoot(self, root, verbose=None):
		if verbose:
			print "[LikeShell] root directory has been set to %s" % (root)
		self.root = root
	
	def mkdir(self, folder=None, verbose=None):
		if not folder:
			folder = self.root
		if folder[0] != '/': # relative path
			folder = self.root+"/"+folder
		if verbose:
			print "[LikeShell] folder %s created" % (folder)
		statement = "mkdir '%s'" % (folder)
		os.system(statement)
	
	def wget(self, url, filename=None, log=None, verbose=None):
		if not log:
			if not filename:
				statement = "cd '%s' && wget -U 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0' '%s'" % (self.root, url)
			else:
				statement = "cd '%s' && wget -U 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0' '%s' -O '%s'" % (self.root, url, filename)
		else:
			if not filename:
				if log[0] != '/': # relative path
					log = self.root+"/"+log
				statement = "cd '%s' && wget -U 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0' '%s' 2>> '%s'" % (self.root, url, log)
			else:
				if log[0] != '/': # relative path
					log = self.root+"/"+log
				statement = "cd '%s' && wget -U 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0' '%s' -O '%s' 2>> '%s'" % (self.root, url, filename, log)
		if verbose:
			print "[LikeShell] Command: %s" % (statement)
		os.system(statement)
