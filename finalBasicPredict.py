"""
Module to get the cookies for devices based on IP Address match
__author__ : SRK @ Kaggle
"""
import csv
import time
import pandas as pd
import numpy as np
from scipy import stats

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

if __name__ == "__main__":
	# file config #
	data_path = "../Data/"
	ip_file = open(data_path+"id_all_ip.csv")

	print "Getting device and IP dict.."
	device_dict, ip_dict = getIPDict(ip_file)
	
	print "Processing Test sample"
	# device test file #
	dict_reader = csv.DictReader(open(data_path + "dev_test_basic.csv"))
	# out file #
	writer = csv.writer(open("sub3.csv","w"))
	writer.writerow(["device_id","cookie_id"])
		
	# There are many IPs with high number of cookies. But from eyeballing the train, it seems not many cookies are associated with a device (mostly upto 3-4 cookies) #
	# So just use those IP values which has less than 4 cookies and get the cookie ids#
	# use the cookie id that appeared the most number of times if there are no IPs with less than 4 cookies #
	row_count = 0
	for row in dict_reader:
		row_count += 1
		device_id = row['device_id']   
		all_cookies_list = []
		select_cookies_list = []
		for ip in device_dict[device_id]:
			try:
				ip_list = ip_dict[ip]
				all_cookies_list.extend(ip_list)
				if len(ip_list) < 4:
					select_cookies_list.append(ip_list)
			except KeyError:
				# some ips are missing.. skipping them.. #
				pass

		# hand made rules #
		if len(select_cookies_list) == 1:
			out_cookies = select_cookies_list[0] 
		elif len(select_cookies_list) > 1:
			temp_list = [cookie for cookie_list in select_cookies_list for cookie in cookie_list]
			out_cookies = [stats.mode(temp_list)[0][0]]
		elif len(select_cookies_list) == 0:
			out_cookies = [stats.mode(all_cookies_list)[0][0]]

		# join the cookie ids with a space and form a string #
		out_cookie_str = ""
		for out_cookie in out_cookies:
			out_cookie_str = out_cookie_str + out_cookie + " "
		out_cookie_str = out_cookie_str.strip()

		# write output #
		writer.writerow([device_id, out_cookie_str])

		# check progress #
		if row_count % 10000==0:
			print "Processed : ", row_count
	
