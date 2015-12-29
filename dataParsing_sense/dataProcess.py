# -*- coding: utf-8 -*- 

import sys
import jieba
import regex as re
reload(sys)
sys.setdefaultencoding('utf-8')    

sys.argv
FROM_LOC = "../webIR/data_tmp/"
TO_LOC = "../webIR/data/"
print ("\033[1;32m  File name: %s \033[0m" % str(sys.argv[1]))
f = open(FROM_LOC + sys.argv[1], 'r')
content = f.read()

jieba.set_dictionary('dict.txt.big')

for ch in ["，", "；", "、", "。", "「", "」"]:
  if ch in content:
    content = content.replace(ch, "")

words = jieba.cut(content, cut_all=False)
content = ' '.join(words)

f2 = open(TO_LOC + sys.argv[1], 'w')
f2.write(content)
