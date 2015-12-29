XmlConverter用法:

	xmlConverter = XmlConverter()
	xmlConverter.convertDoc(0, 10)
使用之前先把Config.py的路徑改一下
標點符號可能沒有剔除完全，有看到沒踢掉的標點符號幫我在remove_punctuation()加一下

Language Model:
	Bigram的公式和參數目前參考這篇 "Optimizing Two–Stage Bigram Language Models for IR" [WWW 2010] 效果還沒好好測試過
