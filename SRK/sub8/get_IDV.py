"""
This file is to create IDVs for building the binary classification model. Our objective is identify the cookies corresponding to the given device id. Number of given cookies is huge and so we cannot create a binary classification data for all the combinations of device_id and cookie_ids.
 
Instead if we could reduce the number of cookies to a reasonable amount before the classification task, then the classification task will be easier. This is similar to negative subsampling task, where we need to remove all the zeros but retain all the ones so as the boost up the DV rate. So the first step is the reduction of number of cookies for binary classification model and the second step is to build a binary classification model.

There are many ways to reduce the number of cookies and one way is to make use of IP address. This code uses IP address based initial screening.
'id_all_ip.csv' file contains info on all the IP address associated with the device and cookie id. Intuitively, if the device and cookie has the same IP address, then there is a very high chance that both of them are related. This rationale is used in this code for initial cookie selection.

Once we reduce the number of device-cookie combinations are reduced by this method, next step is to create the independant variables(IDV) for all these combinations. This file creates some basic IDVs for classification tasks. IDVs are created for all three samples: dev, val and test

Please refer to Mark's detailed comment for understanding the 'getIPDict' function present in this code.

Code summary is as follows:
1. Loop through each line in the dev_DV.csv file where each line has a device id and the associated cookies in the form of list. Please check the dev_DV.csv file once if needed.
2. Get the device id and the list of cookies and store it in a variable
3. Now from device_dict, identify all the IP addresses which have the given device_id
4. Now using ip_dict, get all the cookies that are linked to the IP
5. If the number of cookies linked to an IP is greater than shared_ip_cutoff (=30), skip the IP address. These IPs are considered as shared or public IPs. 30 is an arbitrary number which I came up with. A higher number decreases the number of cookies left out but increases the processing time and vice versa. Please feel free to change this value of 30 to something else and check the difference in the number of rows used for model build and the number of cookies we are missing out.  
6. Store the cookies obtained from the last step in all_cookie_list (type=list) and all_cookie_list_list (type=list of lists)
7. Get the number of occurrence of each of the each cookie and store it in a dict with cookie_id as key and number of occurrence as value.
8. Get the count of number of cookies present in the given sample and the number of cookies that could not be identified through this IP matching rule. We should find a way to include this unidentified cookies. 
9. Now for all the identified cookies, get some simple IDVs and write it into an out file along with DV. Only very simple IDVs are created in this version. There is a very good opportunity to create more useful variables here to boost up our score.

The above code summary is common to all three (dev, val and test) samples

P.S: Sorry guys. I should have made it more modular for easy readability. I will try to do it if you guys find it difficult to follow the code.
"""
import csv
import numpy as np
import pandas as pd

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
	cookie_dict = {}

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
			cookie_dict[row[0]] = ip_list
                        for ip in ip_list:
                                temp_list = ip_dict.get(ip,[])
                                temp_list.append(row[0])
                                ip_dict[ip] = temp_list
                else:
                        print "Device or Cookie has unacceptable value.. Value : ", row[1]
                        raise

                # printing the progress #
                if counter % 100000 == 0:
                        print "Processed : ", counter

        return device_dict, ip_dict, cookie_dict

def getMinMaxMean(cookie, all_cookie_list_list):
	"""
	This function is to identify the lists that have the input cookie and get summary stats on the list such as min, max and mean
	@param cookie : cookie that needs to be searched
	@param all_cookie_list_list : This is list of lists. Each inner list possess one or more cookies
	"""
	# initialing a variable which gets the length of those cookie lists that have the input cookie #
	len_cookie_lists = []
	for cookie_list in all_cookie_list_list:
		if cookie  in cookie_list:
			len_cookie_lists.append(len(cookie_list))
	return [ np.min(len_cookie_lists), np.max(len_cookie_lists), np.mean(len_cookie_lists) ]
			
def getCookieInfoDict(cookie_info_file):
	"""
	Function to get the variables from cookie_all_basic.csv file and store it in a dict
	"""
	cookie_handle = open(cookie_info_file)
        cookie_reader = csv.reader(cookie_handle)
        cookie_reader.next()

        counter = 0
        cookie_info_dict = {}
        for row in cookie_reader:
                counter += 1
                cookie_id = row[1]
                try:
                        cookie_computer_os_type = int( row[2].replace('computer_os_type_','') )
                except Exception,e:
                        print "Computer OS type Exceptions is : ", e
                        cookie_computer_os_type = -999
                try:
                        cookie_computer_browser_version = int( row[3].replace('computer_browser_version_','') )
                except Exception,e:
                        print "Computer browser type Exceptions is : ", e
                        cookie_computer_browser_version = -999
                try:
                        cookie_country = int( row[4].replace('country_','') )
                except Exception,e:
                        print "Country Exceptions is : ", e
                        cookie_country = -999
                try:
                        cookie_anonymous_c0 = int(row[5])
                except Exception,e:
                        print "Anonymous C0 exception : ",e
                        cookie_anonymous_c0 = -999
                try:
                        cookie_anonymous_c1 = int( row[6].replace('anonymous_c1_','') )
                except Exception,e:
                        print "Anonymous C1 exception : ",e
                        cookie_anonymous_c1 = -999
                try:
                        cookie_anonymous_c2 = int( row[7].replace('anonymous_c2_','') )
                except Exception,e:
                        print "Anonymous C2 exception : ",e
                        cookie_anonymous_c2 = -999
                try:
                        cookie_anonymous_5 = int(row[8])
                except Exception,e:
                        print "Anonymous 5 exception : ",e
                        cookie_anonymous_5 = -999
		try:
                        cookie_anonymous_6 = int(row[9])
                except Exception,e:
                        print "Anonymous 6 exception : ",e
                        cookie_anonymous_6 = -999
                try:
                        cookie_anonymous_7 = int(row[10])
                except Exception,e:
                        print "Anonymous 7 exception : ",e
                        cookie_anonymous_7 = -999
                cookie_info_dict[cookie_id] = [cookie_computer_os_type, cookie_computer_browser_version, cookie_country, cookie_anonymous_c0, cookie_anonymous_c1, cookie_anonymous_c2, cookie_anonymous_5, cookie_anonymous_6, cookie_anonymous_7]
	cookie_handle.close()
	return cookie_info_dict


def getDeviceInfoDict(device_file):
	device_handle = open(device_file)
        device_reader = csv.reader(device_handle)
        device_reader.next() # skipping header

        counter = 0
        device_info_dict = {}
        for row in device_reader:
                counter += 1
                device_id = row[1]
                try:
                        device_type = int( row[2].replace('devtype_','') )
                except Exception,e:
                        print "Exception in device type : ", e
                        device_type = -999
                try:
                        device_os = int( row[3].replace('devos_','') )
                except Exception,e:
                        print "Exception in device os type : ", e
                        device_os = -999
                try:
                        device_country = int( row[4].replace('country_','') )
                except Exception,e:
                        print "Exception in device country type : ", e
                        device_country = -999
                try:
                        device_anonymous_c0 = int(row[5])
                except Exception,e:
                        print "Anonymous C0 exception : ",e
                        device_anonymous_c0 = -999
                try:
                        device_anonymous_c1 = int( row[6].replace('anonymous_c1_','') )
                except Exception,e:
                        print "Anonymous C1 exception : ",e
                        device_anonymous_c1 = -999
                try:
                        device_anonymous_c2 = int( row[7].replace('anonymous_c2_','') )
                except Exception,e:
                        print "Anonymous C2 exception : ",e
                        device_anonymous_c2 = -999
                try:
                        device_anonymous_5 = int(row[8])
                except Exception,e:
                        print "Anonymous 5 exception : ",e
                        device_anonymous_5 = -999
		try:
                        device_anonymous_6 = int(row[9])
                except Exception,e:
                        print "Anonymous 6 exception : ",e
                        device_anonymous_6 = -999
                try:
                        device_anonymous_7 = int(row[10])
                except Exception,e:
                        print "Anonymous 7 exception : ",e
                        device_anonymous_7 = -999

                device_info_dict[device_id] = [device_type, device_os, device_country, device_anonymous_c0, device_anonymous_c1, device_anonymous_c2, device_anonymous_5, device_anonymous_6, device_anonymous_7]
	device_handle.close()
	return device_info_dict

def getSummaryCookieIP(cookie_dict, ip_dict):
	cookie_ip_summary_dict = {}
	for cookie in cookie_dict.keys():
		cookie_len_list = []
		for ip in cookie_dict[cookie]:
			try:
                                cookie_list = ip_dict[ip]
                        except KeyError:
                                continue
                        # skipping those ips where there are more number of cookies associated with it, say more than 30 #
                        if len(cookie_list) > 200:
                                continue
			cookie_len_list.append( len(cookie_list) )
		if cookie_len_list:
			cookie_ip_summary_dict[cookie] = [np.min(cookie_len_list), np.max(cookie_len_list), np.mean(cookie_len_list)]
		else:
			cookie_ip_summary_dict[cookie] = [999,999,999]
	return cookie_ip_summary_dict


if __name__ == "__main__":
	# path of the input files #
	data_path = "../../Data/"

	# specify the input files #
	dev_dv_file = data_path + "dev_DV.csv"
	dev_all_rows_file = data_path + "dev_all_rows.csv"
	val_dv_file = data_path + "val_DV.csv"
	val_all_rows_file = data_path + "val_all_rows.csv"
	id_all_ip_file = data_path + "id_all_ip.csv"
	sample_sub_file = data_path + "sampleSubmission.csv"
	test_all_rows_file = data_path + "test_all_rows.csv"
	cookie_file = data_path + "cookie_all_basic.csv"
	device_train_file = data_path + "dev_train_basic.csv"
	device_test_file = data_path + "dev_test_basic.csv"

	# creating a handle for each #
	dev_dv_handle = open(dev_dv_file)
	val_dv_handle = open(val_dv_file)
	id_all_ip_handle = open(id_all_ip_file)
	test_dv_handle = open(sample_sub_file)

	print "Getting device and IP dict.."
        device_dict, ip_dict, cookie_dict = getIPDict(id_all_ip_handle)
	id_all_ip_handle.close()

	print "Getting cookie_ip_summary_dict..."
	cookie_ip_summary_dict = getSummaryCookieIP(cookie_dict, ip_dict)

	print "Getting cookie info dict.."
	cookie_info_dict = getCookieInfoDict(cookie_file)
	
	print "Getting device info dicts.."
	device_train_info_dict = getDeviceInfoDict(device_train_file)
	device_test_info_dict = getDeviceInfoDict(device_test_file)


	shared_ip_cutoff = 30
	val_test_shared_ip_cutoff = 30

	
	###############################         DEV SAMPLE          ###########################################
	print "Getting all rows for dev sample based on IP match.."
	dev_all_rows_handle = open(dev_all_rows_file,"w")
	# initializing file handlers #
	dev_dv_reader = csv.reader(dev_dv_handle)
	dev_all_rows_writer = csv.writer(dev_all_rows_handle)
	# working on headers #
	dev_dv_reader.next()  # skipping the header
	dev_all_rows_writer.writerow(['device_id', 'cookie_id', 'cookie_count', 'num_ip_with_device', 'num_ip_with_cookie', 'ratio_cookie_count_by_num_ip_device', 'ratio_cookie_count_by_num_ip_cookie', 'ratio_num_ip_cookie_by_num_ip_device', 'min_cookie_in_ip', 'max_cookie_in_ip', 'mean_cookie_in_ip', 'cookie_computer_os_type', 'cookie_computer_browser_version', 'cookie_country', 'cookie_anonymous_c0', 'cookie_anonymous_c1', 'cookie_anonymous_c2', 'cookie_anonymous_5', 'cookie_anonymous_6', 'cookie_anonymous_7', 'device_type', 'device_os', 'device_country', 'device_anonymous_c0', 'device_anonymous_c1', 'device_anonymous_c2', 'device_anonymous_5', 'device_anonymous_6', 'device_anonymous_7', 'min_cookie_in_device_ip','max_cookie_in_device_ip','mean_cookie_in_device_ip', 'min_cookie_in_cookie_ip','max_cookie_in_cookie_ip','mean_cookie_in_cookie_ip', 'DV'])
	# initializing the counter variables #
	total_length = 0 # this variable counts the total number of cookies present in the dev sample  
	not_found_length = 0 # this variable counts the number of cookies that are not found by IP match 
	# looping through the dev sample rows #
	for row in dev_dv_reader:
		device_id = row[0]  # first element in the list is device id
		cookie_ids = eval(row[1])  # second element in the list is cookie_ids list
		all_cookie_list = []
		all_cookie_list_list = []
		all_cookie_length_list= []
		for ip in device_dict[device_id]:
			# skip if the ip is not present in the ip_dict #
			try:
				cookie_list = ip_dict[ip]
			except KeyError:
				continue
			# skipping those ips where there are more number of cookies associated with it, say more than 30 #
			if len(cookie_list) > shared_ip_cutoff:
				continue
			# adding the cookie list of current ip to all cookie list #
			all_cookie_list.extend(cookie_list)
			all_cookie_list_list.append(cookie_list)
			all_cookie_length_list.append(len(cookie_list))
		# getting the unique cookies from all the ips #
		all_cookie_set = set(all_cookie_list)
		# get the count of occurrance of cookies in form of dict #
		cookie_count_dict = {}
		for cookie in all_cookie_list:
			cookie_count_dict[cookie] = cookie_count_dict.get(cookie,0) + 1
		# getting the count of total no of cookies in dev and cookies which are not found through ip matching #
		for cookie in cookie_ids:
			total_length += 1
			if cookie not in all_cookie_set:
				not_found_length += 1
		# writing to the all rows files for all the cookies identified through ips along with few variables #
		for cookie in all_cookie_set:
			out_row = []
			out_row.extend([ device_id, cookie, cookie_count_dict[cookie], len(device_dict[device_id]), len(cookie_dict[cookie]), cookie_count_dict[cookie]/float(len(device_dict[device_id])), cookie_count_dict[cookie]/float(len(cookie_dict[cookie])), len(cookie_dict[cookie])/float(len(device_dict[device_id])) ])
			min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip = getMinMaxMean(cookie, all_cookie_list_list)
			out_row.extend([ min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip ])
			out_row.extend( cookie_info_dict[cookie] )
			out_row.extend( device_train_info_dict[device_id] )
			out_row.extend( [np.min(all_cookie_length_list), np.max(all_cookie_length_list), np.mean(all_cookie_length_list)] )
			out_row.extend( cookie_ip_summary_dict[cookie] )
			if cookie in cookie_ids:
				out_row.append(1)
			else:
				out_row.append(0)
			dev_all_rows_writer.writerow(out_row)
	print "Total number of cookies in dev sample : ",total_length
	print "Number of cookies not captured based on IP address match : ",not_found_length	
	# closing the file handlers #
	dev_all_rows_handle.close()
	dev_dv_handle.close()
	


	##################################          VAL SAMPLE              ########################################
        print "Getting all rows for val sample based on IP match.."
	val_all_rows_handle = open(val_all_rows_file,"w")
        val_dv_reader = csv.reader(val_dv_handle)
        val_all_rows_writer = csv.writer(val_all_rows_handle)
        # working on headers #
        val_dv_reader.next()  # skipping the header
        val_all_rows_writer.writerow(['device_id', 'cookie_id', 'cookie_count', 'num_ip_with_device', 'num_ip_with_cookie', 'ratio_cookie_count_by_num_ip_device', 'ratio_cookie_count_by_num_ip_cookie', 'ratio_num_ip_cookie_by_num_ip_device', 'min_cookie_in_ip', 'max_cookie_in_ip', 'mean_cookie_in_ip', 'cookie_computer_os_type', 'cookie_computer_browser_version', 'cookie_country', 'cookie_anonymous_c0', 'cookie_anonymous_c1', 'cookie_anonymous_c2', 'cookie_anonymous_5', 'cookie_anonymous_6', 'cookie_anonymous_7', 'device_type', 'device_os', 'device_country', 'device_anonymous_c0', 'device_anonymous_c1', 'device_anonymous_c2', 'device_anonymous_5', 'device_anonymous_6', 'device_anonymous_7', 'min_cookie_in_device_ip','max_cookie_in_device_ip','mean_cookie_in_device_ip', 'min_cookie_in_cookie_ip','max_cookie_in_cookie_ip','mean_cookie_in_cookie_ip', 'DV'])
        # initializing the counter variables #
        total_length = 0
        not_found_length = 0
        # looping through the val sample rows #
        for row in val_dv_reader:
                device_id = row[0]  # first element in the list is device id
                cookie_ids = eval(row[1])  # second element in the list is cookie_ids list
                all_cookie_list = []
                all_cookie_list_list = []
		all_cookie_length_list = []
                for ip in device_dict[device_id]:
                        # skip if the ip is not present in the ip_dict #
                        try:
                                cookie_list = ip_dict[ip]
                        except KeyError:
                                continue
                        # skipping those ips where there are more number of cookies associated with it, say more than 30 #
                        if len(cookie_list) > val_test_shared_ip_cutoff:
                                continue
                        # adding the cookie list of current ip to all cookie list #
                        all_cookie_list.extend(cookie_list)
                        all_cookie_list_list.append(cookie_list)
			all_cookie_length_list.append(len(cookie_list))
                # getting the unique cookies from all the ips #
                all_cookie_set = set(all_cookie_list)
                # get the count of occurrance of cookies in form of dict #
                cookie_count_dict = {}
                for cookie in all_cookie_list:
                        cookie_count_dict[cookie] = cookie_count_dict.get(cookie,0) + 1
                # getting the count of total no of cookies in val and cookies which are not found through ip matching #
                for cookie in cookie_ids:
                        total_length += 1
                        if cookie not in all_cookie_set:
                                not_found_length += 1
                # writing to the all rows files for all the cookies identified through ips along with few variables # 
                for cookie in all_cookie_set:
                        out_row = []
                        out_row.extend([ device_id, cookie, cookie_count_dict[cookie], len(device_dict[device_id]), len(cookie_dict[cookie]), cookie_count_dict[cookie]/float(len(device_dict[device_id])), cookie_count_dict[cookie]/float(len(cookie_dict[cookie])), len(cookie_dict[cookie])/float(len(device_dict[device_id])) ])
                        min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip = getMinMaxMean(cookie, all_cookie_list_list)
                        out_row.extend([ min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip ])
			out_row.extend( cookie_info_dict[cookie] )
                        out_row.extend( device_train_info_dict[device_id] )
			out_row.extend( [np.min(all_cookie_length_list), np.max(all_cookie_length_list), np.mean(all_cookie_length_list)] )
                        out_row.extend( cookie_ip_summary_dict[cookie] )
                        if cookie in cookie_ids:
                                out_row.append(1)
                        else:
                                out_row.append(0)
                        val_all_rows_writer.writerow(out_row)
        print "Total number of cookies in val sample : ",total_length
        print "Number of cookies not captured based on IP address match : ",not_found_length
        # closing the file handlers #
        val_all_rows_handle.close()
        val_dv_handle.close()



	################################            TEST SET             #####################################################
	print "Getting all rows for test sample based on IP match.."
	test_all_rows_handle = open(test_all_rows_file,"w")
        test_dv_reader = csv.reader(test_dv_handle)
        test_all_rows_writer = csv.writer(test_all_rows_handle)
        # working on headers #
        test_dv_reader.next()  # skipping the header
        test_all_rows_writer.writerow(['device_id', 'cookie_id', 'cookie_count', 'num_ip_with_device', 'num_ip_with_cookie', 'ratio_cookie_count_by_num_ip_device', 'ratio_cookie_count_by_num_ip_cookie', 'ratio_num_ip_cookie_by_num_ip_device', 'min_cookie_in_ip', 'max_cookie_in_ip', 'mean_cookie_in_ip', 'cookie_computer_os_type', 'cookie_computer_browser_version', 'cookie_country', 'cookie_anonymous_c0', 'cookie_anonymous_c1', 'cookie_anonymous_c2', 'cookie_anonymous_5', 'cookie_anonymous_6', 'cookie_anonymous_7', 'device_type', 'device_os', 'device_country', 'device_anonymous_c0', 'device_anonymous_c1', 'device_anonymous_c2', 'device_anonymous_5', 'device_anonymous_6', 'device_anonymous_7', 'min_cookie_in_device_ip','max_cookie_in_device_ip','mean_cookie_in_device_ip', 'min_cookie_in_cookie_ip','max_cookie_in_cookie_ip','mean_cookie_in_cookie_ip', 'DV'])
        # initializing the counter variables #
        total_length = 0
        # looping through the val sample rows #
        for row in test_dv_reader:
                device_id = row[0]  # first element in the list is device id
                all_cookie_list = []
                all_cookie_list_list = []
		all_cookie_length_list = []
                for ip in device_dict[device_id]:
                        # skip if the ip is not present in the ip_dict #
                        try:
                                cookie_list = ip_dict[ip]
                        except KeyError:
                                continue
                        # skipping those ips where there are more number of cookies associated with it, say more than 30 #
                        if len(cookie_list) > val_test_shared_ip_cutoff:
                                continue
                        # adding the cookie list of current ip to all cookie list #
                        all_cookie_list.extend(cookie_list)
                        all_cookie_list_list.append(cookie_list)
			all_cookie_length_list.append(len(cookie_list))
                # getting the unique cookies from all the ips #
                all_cookie_set = set(all_cookie_list)
                # get the count of occurrance of cookies in form of dict #
                cookie_count_dict = {}
                for cookie in all_cookie_list:
                        cookie_count_dict[cookie] = cookie_count_dict.get(cookie,0) + 1
                # writing to the all rows files for all the cookies identified through ips along with few variables # 
                for cookie in all_cookie_set:
                        out_row = []
                        out_row.extend([ device_id, cookie, cookie_count_dict[cookie], len(device_dict[device_id]), len(cookie_dict[cookie]), cookie_count_dict[cookie]/float(len(device_dict[device_id])), cookie_count_dict[cookie]/float(len(cookie_dict[cookie])), len(cookie_dict[cookie])/float(len(device_dict[device_id])) ])
                        min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip = getMinMaxMean(cookie, all_cookie_list_list)
                        out_row.extend([ min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip ])
			out_row.extend( cookie_info_dict[cookie] )
                        out_row.extend( device_test_info_dict[device_id] )
			out_row.extend( [np.min(all_cookie_length_list), np.max(all_cookie_length_list), np.mean(all_cookie_length_list)] )
                        out_row.extend( cookie_ip_summary_dict[cookie] )
                        out_row.append(0)
                        test_all_rows_writer.writerow(out_row)
        # closing the file handlers #
        test_all_rows_handle.close()
        test_dv_handle.close()
