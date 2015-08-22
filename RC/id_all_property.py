# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 21:40:37 2015

@author: rchong
"""

import os
import pandas as pd
import numpy as np
import csv
from itertools import islice
from scipy import stats
import pickle

# Define/Declare functions here
def getIPDict(ip_file):
	"""
	Each line in the IP file belongs to either a device or a cookie.
	This function creates two dictionaries
	1. Device dictionary - has device_id as key and the IPs it belongs to as value in the form of list
	2. IP Dictionary - has IP address as the key and the cookies in that IP as value in the form of list
	Reasoning:
	We need to find the cookies that are associated with the given device in the competition. So given a device we can find out the IP addressess of the device from device dictionary. Then using those IP addresses and IP Dictionary, find out the cookies associated with the IP and link them back to the device.
	"""
	# reading the ip file #
	reader = csv.reader(ip_file)
	header = reader.next()             # skipping the header

	# initializing the dicts #
	device_dict = {}
	ip_dict = {}

	counter = 0                        # counter to manage the progress
	for row in reader:
		counter += 1

		# extracting ip address alone from the given input and store it in a list #
		ip_all_str = ','.join(row[2:]) 
		ip_list = []
		ip_all_list = ip_all_str.replace("{","").replace("}","").replace("),("," ").replace("(","").replace(")","").split(" ")     # formatting 
		for val in ip_all_list:
			ip_list.append(val.split(",")[0])

		# if device, write to device dict, else write to ip dict #
		if row[1] == '0':
			device_dict[row[0]] = ip_list
		elif row[1] == '1':
			for ip in ip_list:
				temp_list = ip_dict.get(ip,[])
				temp_list.append(row[0])
				ip_dict[ip] = temp_list
		else:
			print "Device or Cookie has unacceptable value.. Value : ", row[1]
			raise

		# printing the progress #
		if counter % 50000 == 0:
			print "Processed : ", counter
			
	return device_dict, ip_dict



# Load files that lend themselves to a dataframe
#df_cookie_all_basic = pd.read_csv('cookie_all_basic.csv')
#df_dev_test_basic = pd.read_csv('dev_test_basic.csv')
#df_dev_train_basic = pd.read_csv('dev_train_basic.csv')
#df_ipagg_all = pd.read_csv('ipagg_all.csv')
#df_sample_submission = pd.read_csv('sampleSubmission.csv')

# file config #
#data_path = "../Data/"
#ip_file = open("id_all_ip.csv")


# This stuff works..just commenting out for now
# print "Getting device and IP dict.."
# device_dict, ip_dict = getIPDict(ip_file)

# df_device_dict = pd.DataFrame(list(device_dict.iteritems()), columns=['device_dict_key', 'device_dict_values'])

# df_ip_dict = pd.DataFrame(list(ip_dict.iteritems()), columns=['ip_dict_key', 'ip_dict_values'])

# print(len(device_dict))
# print(df_device_dict.shape)

# print(len(ip_dict))
# print(df_ip_dict)

#ip_file = open("id_all_property.csv")
#print "Getting property dict"
#property_dict = getIPDict(ip(file)

# Define/Declare functions here
# Define/Declare functions here
def getIPDict_2(ip_file):
    """
    Fill in when done
    """
    # reading the ip file #
    reader = csv.reader(ip_file)
    header = reader.next()             # skipping the header

    # initializing the dicts #

    property_dict = {}

    counter = 0

    for row in reader:
        counter += 1
        #print(row[0])

        id_all = row[0]
        indicator = row[1]

        prop_all_str = ','.join(row[2:])

        prop_list = []
        count_list = []

        prop_all_list = prop_all_str.replace("{","").replace("}","").replace("),("," ").replace("(","").replace(")","").split(" ")
        #print(prop_all_list)

        for val in prop_all_list:
            prop_list.append(val.split(",")[0])
            count_list.append(val.split(",")[1])

        #print(prop_list)
        #print(count_list)

        property_dict[id_all] = (indicator, prop_list, count_list)

        # printing the progress #
        if counter % 50000 == 0:
            print "Processed : ", counter

    return property_dict




ip_file = open("id_all_property.csv")
test = getIPDict_2(ip_file)


df_property_dict = pd.DataFrame(list(test.iteritems()), columns=['id_dict_key', 'prop_dict_values'])

file_pickle = open('df_property_dict.pkl', 'w')
pickle.dump(df_property_dict, file_pickle)
