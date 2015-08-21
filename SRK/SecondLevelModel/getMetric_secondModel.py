"""
This module computes the competition metric (F0.5 score) for both the dev and val sample. This also creates the output submission file from the test predictions.
"""
import csv
import numpy as np
import pandas as pd
from sklearn import metrics

#max_num_cookies = 5      # maximum number of cookies to get for a device using secondary method. This number includes UNKNOWN drawbridge handles as well 
#threshold_value = 0.35   # threshold value from the top predicted value till which the search is made. Ex: If the top predicted prob value is 1.0 and threshold is 0.2, get max_num_cookies cookies between 1 and 0.8
#best_cookie_handle_flag = 0 # flag if 1 will get the cookies of only the BEST KNOWN drawbridge handle. If set to 0, will get the cookies of all known drawbridge handle present inside the threshold

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

def getTopNCookies( pred_list_of_lists, n_cookies=5):
	"""
	Function to get the top n cookies from the given list of lists. Each list consists of two elements. First element is the cookie_id and the second element is binary classification score. 
	@param pred_list_of_lists : list of lists of cookies and scores
	@param n_cookies : number of top cookies to get based on score
	"""
	cookie_pred_dict = {}
        for cookie_pred_list in pred_list_of_lists:
                cookie_pred_dict[cookie_pred_list[1]] = cookie_pred_list[0]
        pred_list = []
        key_list = np.sort(cookie_pred_dict.keys())[::-1]
	prev_value = key_list[0]
        for value in key_list[:n_cookies]:
		if prev_value - value < 0.15:
                	pred_list.append(cookie_pred_dict[value])
			#prev_value = value
		else:
			break
	return pred_list

def getDrawbridgePred(pred_list, drawbridge_dict, cookie_draw_dict):
	## Initialization ##
	drawhandle_dict = {}
	drawhandle_list = []

	## getting the drawbridge handle associated witht the predicted cookies and form a dict of drawbridge handles with count being values ##
	## getting the unknown drawbridge handles as separate list ##
	unknown_list = []
	for cookie in pred_list:
		if cookie_draw_dict[cookie] != "-1":
			drawhandle_dict[cookie_draw_dict[cookie]] = drawhandle_dict.get(cookie_draw_dict[cookie],0) + 1
			drawhandle_list.append(cookie_draw_dict[cookie])
		else:
			unknown_list.append(cookie)
	drawhandle_list = list(set(drawhandle_list))

	## getting the handles that have max number of cookies as predictions ##
	## handles are returned as a list since there may be more than one handles with same number of predicted cookies ##
	new_pred_list = []
	max_val = 0
	best_handle_list = []
	for i,key in enumerate(drawhandle_list):
		if drawhandle_dict[key] > max_val:
			best_handle_list = [key]
			max_val = drawhandle_dict[key]
		elif drawhandle_dict[key] == max_val:
			best_handle_list.append(key)

	##  getting all the cookies related to best handles and form a list ##
	if best_handle_list != []:
		new_pred_list = []
		for best_handle in best_handle_list:
			new_pred_list.extend(drawbridge_dict[best_handle])
			#break

	## if there are no best hanldes, use the cookie prediction from unknown handles ##
	## else use the cookies of best handles as such ##
	## This works well for val sample since we know in val sample , there are no handles with -1 is present ##
	## if drawbridge handle = -1 is truly unknown in most of the cases in test set (which I think is the case), then the following framework will owrk ##
	## else it is better to return "new_pred_list + unknown_list" always ##
	## we can try submitting one in each case and compare the results :) ##
	if new_pred_list == []:
		return new_pred_list + unknown_list
	else:
		return new_pred_list
			

def getFScoreFromSecDict(actual_list, pred_list_of_lists, drawbridge_dict, cookie_draw_dict, n_cookies=5):
	"""
	Function to get the F0.5 score from secondary dict
	"""
	pred_list = getTopNCookies( pred_list_of_lists, n_cookies=n_cookies)
	pred_list = getDrawbridgePred(pred_list, drawbridge_dict, cookie_draw_dict)
	return getFScore(actual_list, pred_list)
	
if __name__ == "__main__":
	# input files #
	data_path = "../../Data/"
	dev_dv_file = data_path + "val_develop_DV.csv"
	val_dv_file = data_path + "val_validate_DV.csv"
	test_dv_file = data_path + "sampleSubmission.csv"
	cookie_file = data_path + "cookie_all_basic.csv"
	dev_pred_file = "dev_predictions_m2.csv"
	val_pred_file = "val_predictions_m2.csv"
	test_pred_file = "test_predictions_m2.csv"
	sub_file = "sub21.csv"
	# cutoff for predictions. value above this cutoff are taken as 1 and below are taken as 0 #
	prediction_cutoff = 1.95

	# creating a handle for each #
        dev_dv_handle = open(dev_dv_file)
        val_dv_handle = open(val_dv_file)
	test_dv_handle = open(test_dv_file)
	cookie_file_handle = open(cookie_file)
	dev_pred_handle = open(dev_pred_file)
	val_pred_handle = open(val_pred_file)
	test_pred_handle = open(test_pred_file)
	sub_handle = open(sub_file, "w")

	## getting the cookie drawbridge dict ##
	print "Getting Cookie Draw Dicts"
	drawbridge_dict = {}
	cookie_draw_dict = {}
	cookie_draw_reader = csv.reader(cookie_file_handle)
	cookie_draw_reader.next()
	for row in cookie_draw_reader:
		draw_handle = row[0]
		cookie_id = row[1]
		cookie_draw_dict[cookie_id] = draw_handle
		if draw_handle != "-1":
			temp_list = drawbridge_dict.get(draw_handle,[])
			temp_list.append(cookie_id)
			drawbridge_dict[draw_handle] = temp_list[:]
	drawbridge_dict["-1"] = []
	cookie_file_handle.close()
	

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
			fscore = getFScoreFromSecDict(actual_dev_dict[key], secondary_pred_dev_dict[key], drawbridge_dict, cookie_draw_dict)
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
                        fscore = getFScoreFromSecDict(actual_val_dict[key], secondary_pred_val_dict[key], drawbridge_dict, cookie_draw_dict)
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
			cookie_list = getTopNCookies( secondary_pred_test_dict[device_id] )
			cookie_list = getDrawbridgePred(cookie_list, drawbridge_dict, cookie_draw_dict)
		else:
			cookie_list = ['id_10']
		cookie_list =  " ".join(cookie_list)
		sub_writer.writerow([device_id,  cookie_list])
	test_dv_handle.close()
	sub_handle.close()	
	"""
