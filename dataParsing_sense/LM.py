import sys
import os
import numpy

import Config
from PreProcesser import XmlConverter
from PreProcesser import DocReader
from Modeler import DocModeler

if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('utf8')

	if Config.PRE_PROCESS_ON == 1:
		xmlConverter = XmlConverter()
		#xmlConverter.convertDoc(0, Config.DATA_SIZE)
		xmlConverter.convertQuery(0, Config.QUERY_SIZE)

	else:
		docReader = DocReader()
		docModeler = DocModeler()

		for d in range(0, Config.TEST_DATA_SIZE):
			words = docReader.loadSegDoc(d)
			docModeler.genModelByDocArr(words, d)
			print "Done generate %d model" % (d)

		scoreList = []
		for q in range(5, 6):
			query = docReader.loadQuery(q)
			for d in range(0, Config.TEST_DATA_SIZE):
				score = docModeler.getSpecificScoreByQuery(d, query)
				scoreList.append(score)
				print "d", d, ": ", score

		sortedIdxArr = numpy.argsort(numpy.array(scoreList))
		for i in range(len(sortedIdxArr)-1, len(sortedIdxArr)-4, -1):
			print "Most alike: " + str(sortedIdxArr[i]) + ", value: " + str(scoreList[sortedIdxArr[i]])
	