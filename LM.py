import sys
import numpy
import os

import Config
from PreProcesser import XmlConverter
from PreProcesser import DocReader
from Modeler import DocModeler
from Feedback import FeedbackQueryGenerator

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
		if arg == '-fp':
			Config.FEEDBACK_MODE = 1
		if arg == '-ft':
			Config.FEEDBACK_MODE = 2
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

if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('utf8')

	initDirectories()
	handleArgv()

	if Config.FEEDBACK_MODE == 1:
		feedbackGenerator = FeedbackQueryGenerator()
		feedbackGenerator.genFeedbackQuery()
		sys.exit(0)

	if Config.PRE_PROCESS_ON == 1:
		xmlConverter = XmlConverter()
		xmlConverter.convertDoc(0, Config.DATA_SIZE)
		xmlConverter.convertQuery(0, Config.QUERY_SIZE)

	else:
		docReader = DocReader()
		docModeler = DocModeler()

		for d in range(0, Config.TEST_DATA_SIZE):
			words = docReader.loadSegDoc(d)
			docModeler.genModelByDocArr(words, d)
			print "Done generate %d model" % (d)

		queryResult = []
		for q in range(1, 18):
			scoreList = []
			query = docReader.loadQuery(q)
			for d in range(0, Config.TEST_DATA_SIZE):
				score = docModeler.getSpecificScoreByQuery(d, query)
				scoreList.append(score)
				if d % 100 == 0:
					print "Done %d documents analysis..." % d
			dumpScoreList(q, scoreList)
			queryResult.append( genQueryResult(q, scoreList) )	
		genResultCSV(1, queryResult)
	
