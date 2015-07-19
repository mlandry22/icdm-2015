"""
This module computes the competition metric (F0.5 score) for both the dev and val sample. This also creates the output submission file from the test predictions.
"""
import csv
import numpy as np
import pandas as pd
from sklearn import metrics

def getFScore(actual_list, pred_list):
	"""
	Function to get the F0.5 score
	@param actual_list : actual list of cookies
	@param pred_list : predicted list of cookies
	"""
	num = len( set(actual_list).intersection(set(pred_list)) )
	if num == 0 :
		return 0
	p = num / float(len(pred_list))
	r = num / float(len(actual_list))
	beta_square = 0.25
	coeff = 1.25
	return coeff * ( (p*r) / ((beta_square*p)+r) ) 

def getTopNCookies( pred_list_of_lists, n_cookies=5 ):
	"""
	Function to get the top n cookies from the given list of lists. Each list consists of two elements. First element is the cookie_id and the second element is binary classification score. 
	@param pred_list_of_lists : list of lists of cookies and scores
	@param n_cookies : number of top cookies to get based on score
	"""
	cookie_pred_dict = {}
        for cookie_pred_list in pred_list_of_lists:
                cookie_pred_dict[cookie_pred_list[1]] = cookie_pred_list[0]
        pred_list = []
        key_list = cookie_pred_dict.keys()
        for value in np.sort(key_list)[:n_cookies]:
                pred_list.append(cookie_pred_dict[value])
	return pred_list

def getFScoreFromSecDict(actual_list, pred_list_of_lists, n_cookies=5):
	"""
	Function to get the F0.5 score from secondary dict
	"""
	pred_list = getTopNCookies( pred_list_of_lists, n_cookies=n_cookies)
	return getFScore(actual_list, pred_list)
	
if __name__ == "__main__":
	# input files #
	data_path = "../../Data/"
	dev_dv_file = data_path + "dev_DV.csv"
	val_dv_file = data_path + "val_DV.csv"
	test_dv_file = data_path + "sampleSubmission.csv"
	dev_pred_file = "dev_predictions.csv"
	val_pred_file = "val_predictions.csv"
	test_pred_file = "test_predictions.csv"
	sub_file = "sub5.csv"
	# cutoff for predictions. value above this cutoff are taken as 1 and below are taken as 0 #
	prediction_cutoff = 0.18

	# creating a handle for each #
        dev_dv_handle = open(dev_dv_file)
        val_dv_handle = open(val_dv_file)
	test_dv_handle = open(test_dv_file)
	dev_pred_handle = open(dev_pred_file)
	val_pred_handle = open(val_pred_file)
	test_pred_handle = open(test_pred_file)
	sub_handle = open(sub_file, "w")

	####################         Actual values         ##################
	""" This part of the code creates dictionay for actual values. device_id is the key and cookie_id list is the value """
        print "Getting actual dev dict.."
        dev_dv_reader = csv.reader(dev_dv_handle)
	dev_dv_reader.next() # skipping the header
	actual_dev_dict = {}
	for row in dev_dv_reader:
		device_id = row[0]
		cookie_list = eval(row[1])
		actual_dev_dict[device_id] = cookie_list
	dev_dv_handle.close()

        print "Getting actual val dict.."
        val_dv_reader = csv.reader(val_dv_handle)
        val_dv_reader.next() # skipping the header
        actual_val_dict = {}
        for row in val_dv_reader:
                device_id = row[0]
                cookie_list = eval(row[1])
                actual_val_dict[device_id] = cookie_list
        val_dv_handle.close()


	#####################       Predicted values         ###################
	""" 
	This part of the code creates dictionaries for predicted values.
	'prediction_cutoff' variable is used for the creation of 'pred_sample_dict' (where sample=dev or val or test). If the predcited score is greater than this cutoff, then add the cookie to this dict.
	If the predicted value is lesser than this cutoff, then add the cookie along with its score into a secondary dict 'secondary_pred_sample_dict' (where sample= dev or val or test)
	"""
	print "Getting pred dev dict.."
	dev_pred_reader = csv.DictReader(dev_pred_handle)
	pred_dev_dict = {}
	secondary_pred_dev_dict = {}
	for row in dev_pred_reader:
		device_id = row['device_id']
		cookie_id = row['cookie_id']
		if float(row['prediction']) > prediction_cutoff:
			temp_list = pred_dev_dict.get(device_id, [])
			pred_dev_dict[device_id] = temp_list + [cookie_id]
		else:
			temp_list = secondary_pred_dev_dict.get(device_id, [])
			secondary_pred_dev_dict[device_id] = temp_list + [[cookie_id, float(row['prediction']) ]]
			
	dev_pred_handle.close()

        print "Getting pred val dict.."
        val_pred_reader = csv.DictReader(val_pred_handle)
        pred_val_dict = {}
	secondary_pred_val_dict = {}
        for row in val_pred_reader:
                device_id = row['device_id']
                cookie_id = row['cookie_id']
                if float(row['prediction']) > prediction_cutoff:
                        temp_list = pred_val_dict.get(device_id, [])
                        pred_val_dict[device_id] = temp_list + [cookie_id]
		else:
			temp_list = secondary_pred_val_dict.get(device_id, [])
                        secondary_pred_val_dict[device_id] = temp_list + [[ cookie_id, float(row['prediction']) ]]
        val_pred_handle.close()

	print "Getting pred test dict.."
        test_pred_reader = csv.DictReader(test_pred_handle)
        pred_test_dict = {}
        secondary_pred_test_dict = {}
        for row in test_pred_reader:
                device_id = row['device_id']
                cookie_id = row['cookie_id']
                if float(row['prediction']) > prediction_cutoff:
                        temp_list = pred_test_dict.get(device_id, [])
                        pred_test_dict[device_id] = temp_list + [cookie_id]
                else:
                        temp_list = secondary_pred_test_dict.get(device_id, [])
                        secondary_pred_test_dict[device_id] = temp_list + [[ cookie_id, float(row['prediction']) ]]
        test_pred_handle.close()


	##########################        Getting Evaluation Metric       ##################################
	"""
	This part of the code is to get eval metric (F0.5 score) for dev and val sample.
	If the device_id is present in 'pred_sample_dict' (where sample=dev or val), then use all the cookies which is present in the key-value pair for score calculation
	If the device_id is present in 'secondary_pred_sample_dict', then use the top n cookies for score calculation
	"""
	## Getting the evaluation in dev sample ##
	print "Getting evaluation in dev sample.."
	total_fscore = 0.
	item_count = 0.
	for key in actual_dev_dict:
		item_count += 1
		if pred_dev_dict.has_key(key):
			fscore = getFScore(actual_dev_dict[key], pred_dev_dict[key])
			total_fscore += fscore
		elif secondary_pred_dev_dict.has_key(key):
			fscore = getFScoreFromSecDict(actual_dev_dict[key], secondary_pred_dev_dict[key])
                        total_fscore += fscore
		#if item_count % 1000 == 0:
		#	print "Mean of ", item_count, " is : ", total_fscore / item_count
	print "Mean of ", item_count, " is : ", total_fscore / item_count


	# Getting the evaluation in val sample #
        print "Getting evaluation in val sample.."
        total_fscore = 0.
        item_count = 0.
        for key in actual_val_dict:
                item_count += 1
                if pred_val_dict.has_key(key):
                        fscore = getFScore(actual_val_dict[key], pred_val_dict[key])
                        total_fscore += fscore
		elif secondary_pred_val_dict.has_key(key):
                        fscore = getFScoreFromSecDict(actual_val_dict[key], secondary_pred_val_dict[key])
                        total_fscore += fscore
                #if item_count % 1000 == 0:
                #        print "Mean of ", item_count, " is : ", total_fscore / item_count
	print "Mean of ", item_count, " is : ", total_fscore / item_count


	########################          Writing Submission file          #####################
	"""
	This part of the code is to write the output submission file 
	If the device_id is present in 'pred_sample_dict' (where sample=test), then write all the cookies which is present in the key-value pair into out file
        If the device_id is present in 'secondary_pred_sample_dict', then write the top n cookies for score calculation
	If the device_id is not present at all, write a dummy value ('id_10')
	"""
	# Getting the submission file for test predictions #
	print "Getting the submission file.."
	sub_writer = csv.writer(sub_handle)
	sub_writer.writerow(["device_id","cookie_id"])
	test_dv_reader = csv.reader(test_dv_handle)
        test_dv_reader.next() # skipping the header
        for row in test_dv_reader:
                device_id = row[0]
		if pred_test_dict.has_key(device_id):
			cookie_list = pred_test_dict[device_id]
		elif secondary_pred_test_dict.has_key(device_id):
			cookie_list = getTopNCookies( secondary_pred_test_dict[device_id], n_cookies=5 )
		else:
			cookie_list = ['id_10']
		cookie_list =  " ".join(cookie_list)
		sub_writer.writerow([device_id,  cookie_list])
	test_dv_handle.close()
	sub_handle.close()
		
