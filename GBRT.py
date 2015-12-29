import sys
import numpy
import os
import cPickle

# Import self defined classes
import Config
from PreProcesser import XmlConverter
from PreProcesser import DocReader
from PreProcesser import TrainDataReader
from Modeler import DocModeler
from Modeler import FeatureBasedModeler
from Feedback import FeedbackQueryGenerator

# Import for Gradient boosting classifier
from sklearn.ensemble import GradientBoostingClassifier

def initDirectories():
	# Create directory if necessary
	dirs = ["Temp", Config.MOD_DATA_LOC, "Dump"]
	for d in dirs:
		if not os.path.exists(d):
			os.makedirs(d)

def handleArgv():
	for arg in sys.argv:
		if arg == '-p':
			Config.PRE_PROCESS_ON = 1
		if arg == '-t':
			Config.PRE_PROCESS_ON = 0

def dumpScoreList(q, scoreList):
	if Config.FEEDBACK_MODE == 2:
		scoreFileName = "score_qn"
	else:
		scoreFileName = "score_q"
	with open("Dump/" + scoreFileName + str(q) + ".txt", "wb") as f:
		for i in range(0, len(scoreList)):
			f.write("%d %d\n" % (i, scoreList[i]))
	print "Dump scoreList for query %d" % q

def genQueryResult(q, scoreList):
	sortedIdxArr = numpy.argsort(numpy.array(scoreList))
	resultArr = []
	print "======= Q %d =======" % q
	for i in range(len(sortedIdxArr)-1, len(sortedIdxArr)-101, -1):
		print sortedIdxArr[i], " -> ", scoreList[sortedIdxArr[i]]
		resultArr.append(sortedIdxArr[i])
	return resultArr

def genResultCSV(run, totalQueryResult):
	if Config.FEEDBACK_MODE == 2:
		targetFileName = "phase1_result_feedback.csv"
	else:
		targetFileName = "phase1_result.csv"
	with open(targetFileName, "wb") as f:
		f.write("run,id,rel\n")
		for idx in range(0, len(totalQueryResult) ):
			content = "%d,%d," % (run, idx+1)
			for relID in totalQueryResult[idx]:
				content += "%s " % (relID)
			content = content[0:-1] + '\n'
			f.write(content)

def outputPhase2CSV(clfResults):
        resultCounter = 0
        with open(Config.OUTPUT_SRC_FILE, 'rb') as fr:
            with open("phase2_result.csv", 'wb') as fw:
                lines = fr.readlines()
                for eachLine in lines:
                    if 'NewsId' in eachLine:
                        fw.write('NewsId,Agency\n')
                    else:
                        eachLine = eachLine.replace("\n", "")
                        content = '%s,%s\n' % (eachLine, clfResults[resultCounter])
                        fw.write(content)
                        resultCounter += 1

if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('utf8')

	initDirectories()
	handleArgv()

	if Config.PRE_PROCESS_ON == 1:
		xmlConverter = XmlConverter()
		xmlConverter.convertDoc(0, Config.DATA_SIZE)
		xmlConverter.convertQuery(0, Config.QUERY_SIZE)
                xmlConverter.convertTestData(0, Config.TEST_DATA_SIZE)

	else:
		docReader = DocReader()
		docModeler = DocModeler()
                trainDataReader = TrainDataReader()

                featureModeler = FeatureBasedModeler()
                Y, trainDataIdxs = trainDataReader.getTrainAnswers()
                print "Get Train Answers Done"

                tfidfMat = featureModeler.extractFeaturesMatrix(trainDataIdxs)
                print "Calc data features done"

                X_train = tfidfMat[:len(trainDataIdxs)]
                X_test = tfidfMat[len(trainDataIdxs):]

                if os.path.isfile("clf_gbrt.pkl"):
                    with open('clf_gbrt.pkl', 'rb') as fclf:
                        clf = cPickle.load(fclf)
                else:
                    clf = GradientBoostingClassifier().fit(X_train, Y)
                    print "Done get classifier"

                    with open('clf_gbrt.pkl', 'wb') as fclf:
                        cPickle.dump(clf, fclf)
                        print "Save classifier succussfully"
                
                '''
                # Load test data and gen test model
                testFileNames, testWords = docReader.loadTestDatas(0, Config.TEST_DATA_SIZE)
                testFeatures = []
                for d in range(0, Config.TEST_DATA_SIZE):
                    docModeler.genModelByTestArr(testWords[d], d)
                    testFeatures.append( docModeler.getTestCountFeatures(d) )
                    print "Done Test Feature %d generation" % d
                '''
                testResult = clf.predict(X_test)
                print "Done prediction!"
                    
                outputPhase2CSV(testResult) 
                '''
                # Turn it into features array
                # Put into classifier
                # Get result and output csv


                #featureMat = modeler.extractFeaturesMatrix(rawDocs)
                #print featureMat
                
                '''

		#queryResult = []
		#for q in range(11, 18):
		#	scoreList = []
		#	query = docReader.loadQuery(q)
		#	for d in range(0, Config.TEST_DATA_SIZE):
		#		score = docModeler.getSpecificScoreByQuery(d, query)
		#		scoreList.append(score)
		#		if d % 100 == 0:
		#			print "Done %d documents analysis..." % d
		#	dumpScoreList(q, scoreList)
		#	queryResult.append( genQueryResult(q, scoreList) )	
		#genResultCSV(1, queryResult)
	
