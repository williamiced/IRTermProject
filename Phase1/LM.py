import sys
import os
import numpy

import Config
from PreProcesser import XmlConverter
from PreProcesser import DocReader
from Modeler import DocModeler

def handleArgv():
	for arg in sys.argv:
		if arg == '-p':
			Config.PRE_PROCESS_ON = 1
		if arg == '-t':
			Config.PRE_PROCESS_ON = 0

def genQueryResult(q, scoreList):
	sortedIdxArr = numpy.argsort(numpy.array(scoreList))
	resultArr = []
	for i in range(len(sortedIdxArr)-1, len(sortedIdxArr)-4, -1):
		print sortedIdxArr[i], " -> ", scoreList[sortedIdxArr[i]]
		resultArr.append(sortedIdxArr[i])
	return resultArr

def genResultCSV(run, totalQueryResult):
	with open("phase1_result.csv", "wb") as f:
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

	handleArgv()

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
		for q in range(0, 10):
			scoreList = []
			query = docReader.loadQuery(q)
			for d in range(0, Config.TEST_DATA_SIZE):
				score = docModeler.getSpecificScoreByQuery(d, query)
				scoreList.append(score)
			queryResult.append( genQueryResult(q, scoreList) )	
		genResultCSV(1, queryResult)
	