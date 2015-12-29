import os,shutil
import numpy

directory = "data/"
fileNameList = []
documents = []
targetFileName = "TF_phase1_result.csv"
numd = 163132
numq = 17

for i in range(0, numd+1):
    with open("data/news_story_dataset_modified/" + str(i) + ".txt", "rb") as f:
        documents.append( f.read() )        
for i in range(1, numq+1):
    with open("data/news_story_dataset_modified/q" + str(i) + ".txt", "rb") as f:
        documents.append( f.read() )
documents = tuple(documents)

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
print tfidf_matrix.shape

from sklearn.metrics.pairwise import cosine_similarity
totalList = []
queryResult = []

simResults = cosine_similarity(tfidf_matrix[numd+1:numd+numq+1], tfidf_matrix[0:numd+1])

for scoreList in simResults:
    sortedIdxArr = numpy.argsort(numpy.array(scoreList))
    totalList.append(scoreList)
    resultArr = []
    for i in range(len(sortedIdxArr)-1, len(sortedIdxArr)-101, -1):
        #print sortedIdxArr[i], " -> ", scoreList[sortedIdxArr[i]]
        resultArr.append(sortedIdxArr[i])
    queryResult.append(resultArr)

with open(targetFileName, "wb") as f:
    f.write("run,id,rel\n")
    for idx in range(0, len(queryResult) ):
        content = "%d,%d," % (1, idx+1)
        for relID in queryResult[idx]:
            content += "%s " % (relID)
        content = content[0:-1] + '\n'
        f.write(content)
