# -*- coding: utf-8 -*-

import os
import math
import Config

class DocModeler:
	docCountModels = {}
	collectionCountModel = {}
	vocabularySize = 0
	collectionSize = 0

	def saveModel(self, idx, model):
		if Config.BIG_DATA_MODE_ON:
			if not os.path.exists("Temp"):
				os.makedirs("Temp")
			
			with open("Temp/" + str(idx) + ".mdl", "wb" ) as f:
				for key, value in model.items():
					f.write("%s，%s，%d\n" % (key[0], key[1], value))
		else:
			self.docCountModels[idx] = model

	def getModel(self, idx):
		if Config.BIG_DATA_MODE_ON:
			model = {}
			with open("Temp/" + str(idx) + ".mdl", "rb" ) as f:
				content = f.readlines()
				for item in content:
					records = item.split("，")
					model[(records[0], records[1])] = int (records[2])
			return model
		else:
			return self.docCountModels[idx]

	def genModelByDocArr(self, doc, idx):
		newCountModel = {}
		preWord = ""

		# This is represented as length of document
		newCountModel["", ""] = 0
		for word in doc:
			# Count for bigram
			if preWord is not "":
				if (preWord, word) in newCountModel:
					newCountModel[(preWord, word)] += 1
				else:
					newCountModel[(preWord, word)] = 1
				if (preWord, word) in self.collectionCountModel:
					self.collectionCountModel[(preWord, word)] += 1
				else:
					self.collectionCountModel[(preWord, word)] = 1

			# Count for unigram
			if ("", word) in newCountModel:
				newCountModel[("", word)] += 1
			else:
				newCountModel[("", word)] = 1
			if ("", word) in self.collectionCountModel:
				self.collectionCountModel[("", word)] += 1
			else:
				self.collectionCountModel[("", word)] = 1
				self.vocabularySize += 1
			
			self.collectionSize += 1
			newCountModel["", ""] += 1
			# Update previous word
			preWord = word

		self.saveModel(idx, newCountModel)

	def examineCollection(self):
		for key, value in self.collectionCountModel.items():
			print key, " -> ", value

	def examineModel(self, idx):
		model = self.getModel(idx)
		for key, value in model.items():
			print key[0], " -> ", key[1], ": ", value

	def getJelinekMercerSmoothingScore(self, idx, wp, w):
		model = self.getModel(idx)
		f_w_D = 0
		if ("", w) in model:
			f_w_D = model[("", w)]

		f_wp_w_D = 0
		if (wp, w) in model:
			f_wp_w_D = model[(wp, w)]

		f_wp_D = 0
		if ("", wp) in model:
			f_wp_D = model[("", wp)]

		f_w_C = 0
		if ("", w) in self.collectionCountModel:
			f_w_C = self.collectionCountModel[("", w)]

		f_wp_w_C = 0
		if (wp, w) in self.collectionCountModel:
			f_wp_w_C = self.collectionCountModel[(wp, w)]

		f_wp_C = 0
		if ("", wp) in self.collectionCountModel:
			f_wp_C = self.collectionCountModel[("", wp)]

		f1 = (1-Config.LAMBDA_2) * (f_w_D + Config.MU_1 / self.vocabularySize) / (model["", ""] + Config.MU_1)
		f2 = Config.LAMBDA_2 * (f_wp_w_D + Config.MU_2 / (self.vocabularySize * self.vocabularySize) ) / (f_wp_D + Config.MU_2)
		f3 = (1-Config.LAMBDA_3) * (f_w_C + Config.MU_3 / self.vocabularySize) / (self.collectionSize + Config.MU_3)
		f4 = Config.LAMBDA_3 * (f_wp_w_C + Config.MU_4 / (self.vocabularySize * self.vocabularySize) ) / (f_wp_C + Config.MU_4)
		return (1-Config.LAMBDA_1)*(f1+f2) + Config.LAMBDA_1*(f3+f4)

	def getSpecificScoreByQuery(self, idx, query):
		preWord = ""
		prob = -1
		count = 0
		for word in query:
			curFactor = self.getJelinekMercerSmoothingScore(idx, preWord, word)
			prob += math.log(curFactor)
			preWord = word
		return prob

	def __init__(self):
		print "Generating DocModeler..."
		# do Nothing