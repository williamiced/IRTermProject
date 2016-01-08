# Use Python 
PC=python

# Default 
all: finalPreProcess
run: finalGBRT

phase1_pre: runPreProcess

phase2_pre: finalPreProcess

run_phase1_LM: runLanguageModel

run_phase1_BOW: runBagOfWords

run_phase2_Tree: finalGBRT

runPreProcess:
	$(PC) LM.py -p

runLanguageModel:
	$(PC) LM.py -t && $(PC) LM.py -fp && $(PC) LM.py -ft

runBagOfWords:
	$(PC) tf-idf-new.py

finalPreProcess:
	$(PC) GBRT.py -p

finalGBRT:
	$(PC) GBRT.py -t

