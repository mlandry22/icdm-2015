"""
Split the train sample drawbridge handles into development and validation samples for model building 
Dev-Val split is 80%-20% 
Write the devices into two separate files 
"""
# importing the necessary modules #
import csv
import numpy as np
import pandas as pd
from sklearn.cross_validation import KFold

# location of the input files #
data_path = "../../Data/"
# specification of input and output files #
train_reader = csv.reader(open(data_path+"dev_train_basic.csv"))
dev_writer = csv.writer(open(data_path+"dev_dev_basic.csv","w"))
val_writer = csv.writer(open(data_path+"dev_val_basic.csv","w"))

# getting the unique drawbridge handles from the input train file #
train_drawbridge_handle = np.unique(pd.read_csv(data_path+"dev_train_basic.csv")["drawbridge_handle"])
# splitting the drawbridge handles into two - dev and val at 80-20 ratio #
kf = KFold(train_drawbridge_handle.shape[0], n_folds=5, shuffle=True, random_state=2015)
for dev_index, val_index in kf:
	dev_drawbridge = train_drawbridge_handle[dev_index]
	val_drawbridge = train_drawbridge_handle[val_index]
	break

# reading and writing the header files #
header = train_reader.next()
dev_writer.writerow(header)
val_writer.writerow(header)

# writing the content of dev_train_basic.csv into two files #
for row in train_reader:
	if row[0] in dev_drawbridge:
		dev_writer.writerow(row)
	elif row[0] in val_drawbridge:
		val_writer.writerow(row)
	else:
		print "Drawbridge not in dev and val samples.. Something wrong.. Exiting..!"
		raise
