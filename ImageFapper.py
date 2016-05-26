# -*- coding: utf-8 -*-
import MySQLdb
import time
import os
import threading
import MySQLdb
import time
import requests
import base64
import requests
from pyquery import PyQuery
import json
import re
from LikeShell import LikeShell

class ImageFapper:
	def __init__(self, keyword, root="/root"):
		self.dbHost = ""
		self.dbUsername = ""
		self.dbPassword = ""
		self.dbName = ""
		self.root = root
		self.keyword = keyword
		self.tablename = self.keyword.replace(" ", "_")
		self.baseurl = "http://www.imagefap.com/gallery.php?type=1&userid=&gen=0&search=%s&perpage=10000" % (self.keyword.replace(" ", "%20"))
		
		statement = "CREATE TABLE IF NOT EXISTS `%s_galleries` (\
			`gID` int(11) NOT NULL,\
			`gLink` text NOT NULL,\
			`gTitle` text NOT NULL,\
			`gPics` int(11) NOT NULL,\
			`processed` int(11) NOT NULL,\
			PRIMARY KEY (`gID`)\
			) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Gallary Links for Query \"%s\"';" % (self.tablename, self.keyword)
		c = MySQLdb.connect(host=self.dbHost,user=self.dbUsername,passwd=self.dbPassword,db=self.dbName,charset="utf8")
		cur = c.cursor()
		try:
			cur.execute(statement)
			c.commit()
		except:
			print "Creation of table \"%s_galleries\" failed due to unknown reason" % (self.tablename)
			c.rollback()
		cur.close()
		c.close()
	
	def NextPage(self, q):
		nextlink = "just fuckin' nothin'"
		for each in q('a.link3').items():
			if re.search(r'next',each.text()):
				nextlink = each.attr.href
		if re.search(r'page=\d+',nextlink):
			return re.search(r'\d+',re.search(r'page=\d+',nextlink).group()).group()
		else:
			return None
	
	def addGallary2DB(self, gID, gLink, gTitle, gPics):
		statement = "INSERT INTO `%s_galleries` VALUES ('%s', '%s', '%s', '%s', '0');" % (self.tablename, gID, gLink, gTitle, gPics)
		c = MySQLdb.connect(host=self.dbHost,user=self.dbUsername,passwd=self.dbPassword,db=self.dbName,charset="utf8")
		cur = c.cursor()
		try:
			cur.execute(statement)
			c.commit()
		except:
			print "Insertion of gID %s failed due to unknown reason" % (gID)
			c.rollback()
		cur.close()
		c.close()
		
	def getGallery(self):
		statement = "SELECT * FROM `%s_galleries` WHERE `processed` = 0 LIMIT 1 " % (self.tablename)
		c = MySQLdb.connect(host=self.dbHost,user=self.dbUsername,passwd=self.dbPassword,db=self.dbName,charset="utf8")
		cur = c.cursor()
		try:
			queryResult = cur.execute(statement)
			c.commit()
		except:
			print "Retrival of the Gallery content failed due to unknown reason"
			c.rollback()
			
		if queryResult == 1:
			for items in cur.fetchall():
				gID = items[0]
				gLink = items[1]
				gTitle = items[2]
				gPics = items[3]
				
			statement="UPDATE `%s_galleries` SET `processed` = '2' WHERE `gID` = %s;" % (self.tablename, gID)
			c = MySQLdb.connect(host=self.dbHost,user=self.dbUsername,passwd=self.dbPassword,db=self.dbName,charset="utf8")
			cur = c.cursor()
			try:
				queryResult = cur.execute(statement)
				c.commit()
			except:
				print "Settin' the 'processed' of gID %s to 2 failed due to unknown reason" % (gID)
				c.rollback()
			cur.close()
			c.close()
			return [gID, gLink, gTitle, gPics]
		else:
			cur.close()
			c.close()
			return None
	
	def setGallery2Finished(self, gID):
		statement="UPDATE `%s_galleries` SET `processed` = '1' WHERE `gID` = %s;" % (self.tablename, gID)
		c = MySQLdb.connect(host=self.dbHost,user=self.dbUsername,passwd=self.dbPassword,db=self.dbName,charset="utf8")
		cur = c.cursor()
		try:
			queryResult = cur.execute(statement)
			c.commit()
		except:
			print "Settin' the 'processed' of gID %s to 1 failed due to unknown reason" % (gID)
			c.rollback()
		cur.close()
		c.close()
	
	'''
	def convert(s):
		def r(a,b):
			global s
			s = s.replace(a,b)
		
		SpecialCharList = "\"*/:><?\|"
		SpecialCharList2 = u"＂＊／：＞＜？＼｜"
		map(r,SpecialCharList,SpecialCharList2)
		return s
	'''
	
	def stage1(self):
		r = requests.get(self.baseurl)
		q = PyQuery(r.content)
		for each in q('div.gallerylist table tr').items():
			if each.attr.id:
				gID = each.attr.id
				gTitle = each('td a b').text().replace('\'','\\\'')
				gLink = "http://www.imagefap.com/gallery.php?gid=%s&view=2" % (gID)
				gPics = each('td').eq(1).text()
				print "Insertin' %s | %s | %s | %s" % (gID, gTitle, gLink, gPics)
				self.addGallary2DB(gID, gLink, gTitle, gPics)
		nextPage = self.NextPage(q)
		
		while nextPage:
			link = self.baseurl+"&page="+str(nextPage)
			r = requests.get(link)
			q = PyQuery(r.content)
			for each in q('div.gallerylist table tr').items():
				if each.attr.id:
					gID = each.attr.id
					gTitle = each('td a b').text()
					gLink = "http://www.imagefap.com/gallery.php?gid=%s&view=2" % (gID)
					gPics = each('td').eq(1).text()
					print "Insertin' %s | %s | %s | %s" % (gID, gTitle, gLink, gPics)
					self.addGallary2DB(gID, gLink, gTitle, gPics)
			nextPage = self.NextPage(q)
		
	def stage2(self):
		items = self.getGallery()
		gID = items[0]
		gLink = items[1]
		gTitle = items[2]
		gPics = items[3]
		ls = LikeShell("%s/%s" % (self.root, gTitle))
		ls.mkdir(verbose=1)
		r = requests.get(gLink)
		q = PyQuery(r.content)
		for each in q('tr td table tr td center div form table tr td table tr td a').items():
			imageLink = "http://www.imagefap.com"+each.attr.href
			r2 = requests.get(imageLink)
			q2 = PyQuery(r2.content)
			imageLink4DL = q2('img#mainPhoto').attr.src
			imageFilename = q2('img#mainPhoto').attr.title
			print imageLink4DL
			print imageFilename
			ls.wget(imageLink4DL, filename=imageFilename, log="log.txt", verbose=1)
		self.setGallery2Finished(gID)
		
	def processLink(self, link):
		ls = LikeShell("%s/%s" % (self.root, "2333366666"))
		ls.mkdir(verbose=1)
		r = requests.get(link)
		q = PyQuery(r.content)
		for each in q('tr td table tr td center div form table tr td table tr td a').items():
			imageLink = "http://www.imagefap.com"+each.attr.href
			r2 = requests.get(imageLink)
			q2 = PyQuery(r2.content)
			imageLink4DL = q2('img#mainPhoto').attr.src
			imageFilename = q2('img#mainPhoto').attr.title
			print imageLink4DL
			print imageFilename
			ls.wget(imageLink4DL, filename=imageFilename, log="log.txt", verbose=1)
