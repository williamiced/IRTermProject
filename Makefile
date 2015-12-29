# Use Python 
PC=python

all: finalPreProcess

test: runLanguageModel

run: finalGBRT

feedback:
	$(PC) LM.py -fp && $(PC) LM.py -ft

runPreProcess:
	$(PC) LM.py -p

runLanguageModel:
	$(PC) LM.py -t && $(PC) LM.py -fp && $(PC) LM.py -ft

finalPreProcess:
	$(PC) GBRT.py -p

finalGBRT:
	$(PC) GBRT.py -t

cleanCLF:
	rm clf.pkl
