# -*- coding: utf-8 -*-

import os
import math
import Config
import cPickle
import numpy as np

from scipy.sparse import vstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split


class DocModeler:
	docCountModels = {}
        testCountModels = {}
	collectionCountModel = {}
	vocabularySize = 0
	collectionSize = 0

	def saveModel(self, idx, model):
		if Config.BIG_DATA_MODE_ON:
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

        def getCountFeatures(self, idx):
                model = self.getModel(idx)
                features = []
                for key, value in self.collectionCountModel.items():
                    if key in model:
                        fV = float(model[key]) / value
                    else:
                        fV = 0.0
                    features.append(fV)
                return features

        def getTestCountFeatures(self, idx):
                model = self.testCountModels[idx]
                features = []
                for key, value in self.collectionCountModel.items():
                    if key in model:
                        fV = float(model[key]) / value
                    else:
                        fV = 0.0
                    features.append(fV)
                return features
                
        def genModelByTestArr(self, testData, idx):
                newCountModel = {}
                preWord = ""
                newCountModel["", ""] = 0
                for word in testData:
			# Count for bigram
                        if preWord is not "":
				if (preWord, word) in newCountModel:
					newCountModel[(preWord, word)] += 1
				else:
					newCountModel[(preWord, word)] = 1
			# Count for unigram
			if ("", word) in newCountModel:
				newCountModel[("", word)] += 1
			else:
				newCountModel[("", word)] = 1
			newCountModel["", ""] += 1
			# Update previous word
			preWord = word
                self.testCountModels[idx] = newCountModel
                            
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
			f_wp_w_D += model[(wp, w)]
		if Config.BI_TERM_ON and (w, wp) in model:
			f_wp_w_D += model[(w, wp)]

		f_wp_D = 0
		if ("", wp) in model:
			f_wp_D = model[("", wp)]

		f_w_C = 0
		if ("", w) in self.collectionCountModel:
			f_w_C = self.collectionCountModel[("", w)]

		f_wp_w_C = 0
		if (wp, w) in self.collectionCountModel:
			f_wp_w_C += self.collectionCountModel[(wp, w)]
		if Config.BI_TERM_ON and (w, wp) in self.collectionCountModel:
			f_wp_w_C += self.collectionCountModel[(w, wp)]

		f_wp_C = 0
		if ("", wp) in self.collectionCountModel:
			f_wp_C = self.collectionCountModel[("", wp)]

		f1 = (1-Config.LAMBDA_2) * (f_w_D + Config.MU_1 / self.vocabularySize) / (model["", ""] + Config.MU_1)
		f2 = Config.LAMBDA_2 * (f_wp_w_D + Config.MU_2 / (self.vocabularySize * self.vocabularySize) ) / (f_wp_D + Config.MU_2)
		f3 = (1-Config.LAMBDA_3) * (f_w_C + Config.MU_3 / self.vocabularySize) / (self.collectionSize + Config.MU_3)
		f4 = Config.LAMBDA_3 * (f_wp_w_C + Config.MU_4 / (self.vocabularySize * self.vocabularySize) ) / (f_wp_C + Config.MU_4)
		return (1-Config.LAMBDA_1)*(f1+f2) + Config.LAMBDA_1*(f3+f4)

	def getJelinekMercerSmoothingScoreUnigram(self, idx, wp, w):
		return (1-Config.LAMBDA_1) * f_w_D / model["", ""] + Config.LAMBDA_1 * f_w_C / self.collectionSize

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


class FeatureBasedModeler:
    collectionDict = {}

    def extractFeaturesMatrix(self, trainDataIdxs, Y):
        rawDocs = []
        rawTests = []
        
        if os.path.isfile("tfidf_raw.pkl"):
            with open("tfidf_raw.pkl", 'rb') as f:
                tfidf = cPickle.load(f)
        else:
            for idx in trainDataIdxs:
                with open(Config.MOD_DATA_LOC + str(idx) + '.txt', 'rb') as f:
                    rawDocs.append( f.read() )
                    print "Train Data # %d loaded" % (idx)
            trainDataSize = len(trainDataIdxs)
 
            vectorizer = TfidfVectorizer(ngram_range=(1, 1), min_df=0.00005)
            vectorizer.fit( rawDocs )

            tfidf_train = vectorizer.transform( rawDocs )

            with open(Config.OUTPUT_SRC_FILE, 'rb') as ftemplate:
                templateLines = ftemplate.readlines()
                for templateLine in templateLines:
                    if 'NewsId' in templateLine:
                        continue
                    else:
                        testFileName = templateLine.replace('\n', '')
                        testFilePath = Config.TEST_DATA_MODIFIED_LOC + testFileName + '.txt'
                        with open(testFilePath, 'rb') as ftest:
                            rawTests.append( ftest.read() )
                            print "Test Data %s loaded" % (testFileName)
        
            tfidf_test = vectorizer.transform( rawTests )
            tfidf = vstack([tfidf_train, tfidf_test])

            with open("tfidf_raw.pkl", 'wb') as f:
                cPickle.dump(tfidf, f)
                print "Save TFIDF file successfully"
    
        print tfidf.shape
        Y_train = Y
        '''
        words = vectorizer.get_feature_names()
        for i in xrange(len(rawDocs)):
            print '----Document %d----' % (i)
            for j in xrange(len(words)):
                if tfidf[i,j] > 1e-5:
                    print words[j].encode('utf-8'), tfidf[i,j]
        '''
        return tfidf, Y_train

    def csr_vappend(self, a, b):
        a.data = np.hstack((a.data,b.data))
        a.indices = np.hstack((a.indices,b.indices))
        a.indptr = np.hstack((a.indptr,(b.indptr + a.nnz)[1:]))
        a._shape = (a.shape[0]+b.shape[0],b.shape[1])
        return a

    def __init__(self):
        print "Generating FeatureBasedModeler..."

     
