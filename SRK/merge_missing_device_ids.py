import csv
import numpy as np
import pandas as pd

if __name__ == "__main__":
	missing_device_id_file = "missing_low_device_ids.csv"
	actual_predicions = "sub22.csv"          # our best prediction file
	missing_predictions = "sub23.csv"        # files from which the predictions need to be plugges
	sub_file = "sub24.csv"                   # name of the new submission file

	missing_device_ids = set(np.array(pd.read_csv(missing_device_id_file)["missing_low_device_ids"]))
	#print missing_device_ids
	#print "id_2631023" in missing_device_ids

	reader1 = csv.reader(open(actual_predicions))
	reader2 = csv.reader(open(missing_predictions))
	writer = csv.writer(open(sub_file,"w"))

	writer.writerow(reader1.next())
	reader2.next()

	for row1 in reader1:
		row2 = reader2.next()
		assert row1[0] == row2[0]
		if row1[0] in missing_device_ids:
			print row1[1], "is replaced with", row2[1]
			row1[1] = row2[1]
		writer.writerow(row1)
		
