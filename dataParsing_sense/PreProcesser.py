# -*- coding: utf-8 -*-

import xml.etree.ElementTree
import jieba
import regex as re
import Config
import sys

reload(sys)  
sys.setdefaultencoding('utf-8')
class XmlConverter:
	rawHeader = Config.RAW_DATA_LOC
	modifiedHeader = Config.MOD_DATA_LOC

	def remove_punctuation(self, text):
		for ch in ["，", "；", "、", "。", "「", "」", "／", "：", "《", "》", "？", "◎", "！", "％", "（", "）", "●", "\n", "★", "．", "\r", " ", ".", "%", "~", "-", "+", "『", "』", ",", "(", ")", "︰"]:
			if ch in text:
				text = text.replace(ch, "")
		return text

	def convertDoc(self, fromIdx, toIdx):
		for i in range(fromIdx, toIdx):
			# Read raw data from xml file
			root = xml.etree.ElementTree.parse(Config.RAW_DATA_LOC + str(i) + '.xml').getroot()
			doc = root[0]
			try:
				content = doc.attrib['title'] + doc[0].text
			except:
				content = ""

			# Do jieba process and form a resulted string
			content = self.remove_punctuation(content)
			words = jieba.cut(content, cut_all=False)
			content = ' '.join(words)

			# Save it into txt file
			with open(self.modifiedHeader + str(i) + '.txt', 'wb') as f:
				f.write(content)

			print "Done convert %d.xml" % (i)

	def convertQuery(self, fromIdx, toIdx):
		root = xml.etree.ElementTree.parse(Config.QUERY_FILE_LOC).getroot()
		for i in range(fromIdx, toIdx):
			queryText = ""
			for doc in root[i]:
#				try:
			        queryText += (doc.attrib['title'] + doc[0].text)
#				except:
#					pass
			
			# Do jieba process and form a resulted string
			queryText = self.remove_punctuation(queryText)
			words = jieba.cut(queryText, cut_all=False)
			queryText = ' '.join(words)

			with open(self.modifiedHeader + 'q' + str(i+1) + '.txt', 'wb') as f:
				f.write(queryText)

			print "Done convert query %d" % (i+1)

	def __init__(self):
		# Set Jieba to use traditional chinese dictionary
		jieba.set_dictionary('dict.txt.big')

class DocReader:
	dataHeader = Config.MOD_DATA_LOC

	def remove_punctuation(self, text):
		for ch in ["，", "；", "、", "。", "「", "」", "／", "：", "《", "》", "？", "◎", "！", "％", "（", "）", "●", "\n", "★", "．", "\r", " ", ".", "%", "~", "-", "+", "『", "』", ",", "(", ")", "︰"]:
			if ch in text:
				text = text.replace(ch, "")
		return text

	def loadQuery(self, idx):
		content = open(self.dataHeader + 'q' + str(idx) + '.txt', 'rb').read()
		words = content.split(" ")
		return words

	def loadSegDoc(self, idx):
		content = open(self.dataHeader + str(idx) + '.txt', 'rb').read()
		words = content.split(" ")
		return words

		
