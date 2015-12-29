import Config

class FeedbackQueryGenerator:
	def genFeedbackQuery(self):
		with open("phase1_result.csv", "rb") as fr:
			content = fr.readlines()
			firstLine = True
			for line in content:
				if firstLine:
					firstLine = False
					continue
				cols = line.split(",")
				ids = cols[2].replace("\n", "").split(" ")

				with open(Config.MOD_DATA_LOC + "qn" + cols[1] + ".txt", "wb") as fw:
					# Write the original query into new query
					with open(Config.MOD_DATA_LOC + "q" + cols[1] + ".txt", "rb") as fq:
						fw.write(fq.read())

					# Write RELEVANCE_SIZE of generated result to make new query
					for i in range(0, min(Config.RELEVANCE_SIZE, len(ids)) ):
						with open(Config.MOD_DATA_LOC + ids[i] + ".txt", "rb") as fd:
							fw.write(" " + fd.read())
		print "Done generate feedback queue"

