# -*- coding: utf-8 -*-

import jieba
import regex as re
import Config

class XmlConverter:
	rawHeader = Config.RAW_DATA_LOC
	modifiedHeader = Config.MOD_DATA_LOC

	def remove_punctuation(self, text):
		for ch in ["，", "；", "、", "。"]:
			if ch in text:
				text = text.replace(ch, "")
		return text

	def convertDoc(self, fromIdx, toIdx):
		for i in range(fromIdx, toIdx):
			# Read raw data from xml file
			with open(self.rawHeader + str(i) + '.xml', 'rb') as f:
				content = f.read()

			# Get the target text from xml
			startPos = content.find('<text>')
			endPos = content.find('</text>')
			content = content[startPos + 6: endPos]

			# Do jieba process and form a resulted string
			content = self.remove_punctuation(content)
			words = jieba.cut(content, cut_all=False)
			content = ' '.join(words)

			# Save it into txt file
			with open(self.modifiedHeader + str(i) + '.txt', 'wb') as f:
				f.write(content)

			print "Done convert %d.xml" % (i)

