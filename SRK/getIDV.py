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
	len_cookie_lists = []
	for cookie_list in all_cookie_list_list:
		if cookie  in cookie_list:
			len_cookie_lists.append(len(cookie_list))
	return [ np.min(len_cookie_lists), np.max(len_cookie_lists), np.mean(len_cookie_lists) ]
			

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

	# creating a handle for each #
	dev_dv_handle = open(dev_dv_file)
	dev_all_rows_handle = open(dev_all_rows_file,"w")
	val_dv_handle = open(val_dv_file)
	val_all_rows_handle = open(val_all_rows_file,"w")
	id_all_ip_handle = open(id_all_ip_file)
	test_dv_handle = open(sample_sub_file)
	test_all_rows_handle = open(test_all_rows_file,"w")

	print "Getting device and IP dict.."
        device_dict, ip_dict, cookie_dict = getIPDict(id_all_ip_handle)
	id_all_ip_handle.close()


	print "Getting all rows for dev sample based on IP match.."
	dev_dv_reader = csv.reader(dev_dv_handle)
	dev_all_rows_writer = csv.writer(dev_all_rows_handle)
	# working on headers #
	dev_dv_reader.next()  # skipping the header
	dev_all_rows_writer.writerow(['device_id', 'cookie_id', 'cookie_count', 'num_ip_with_device', 'num_ip_with_cookie', 'ratio_cookie_count_by_num_ip_device', 'ratio_num_ip_cookie_by_num_ip_device', 'min_cookie_in_ip', 'max_cookie_in_ip', 'mean_cookie_in_ip', 'DV'])
	# initializing the counter variables #
	total_length = 0 
	not_found_length = 0
	# looping through the dev sample rows #
	for row in dev_dv_reader:
		device_id = row[0]  # first element in the list is device id
		cookie_ids = eval(row[1])  # second element in the list is cookie_ids list
		all_cookie_list = []
		all_cookie_list_list = []
		for ip in device_dict[device_id]:
			# skip if the ip is not present in the ip_dict #
			try:
				cookie_list = ip_dict[ip]
			except KeyError:
				continue
			# skipping those ips where there are more number of cookies associated with it, say more than 30 #
			if len(cookie_list) > 30:
				continue
			# adding the cookie list of current ip to all cookie list #
			all_cookie_list.extend(cookie_list)
			all_cookie_list_list.append(cookie_list)
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
			out_row.extend([ device_id, cookie, cookie_count_dict[cookie], len(device_dict[device_id]), len(cookie_dict[cookie]), cookie_count_dict[cookie]/float(len(device_dict[device_id])), len(cookie_dict[cookie])/float(len(device_dict[device_id])) ])
			min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip = getMinMaxMean(cookie, all_cookie_list_list)
			out_row.extend([ min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip ])
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


        print "Getting all rows for val sample based on IP match.."
        val_dv_reader = csv.reader(val_dv_handle)
        val_all_rows_writer = csv.writer(val_all_rows_handle)
        # working on headers #
        val_dv_reader.next()  # skipping the header
        val_all_rows_writer.writerow(['device_id', 'cookie_id', 'cookie_count', 'num_ip_with_device', 'num_ip_with_cookie', 'ratio_cookie_count_by_num_ip_device', 'ratio_num_ip_cookie_by_num_ip_device', 'min_cookie_in_ip', 'max_cookie_in_ip', 'mean_cookie_in_ip', 'DV'])
        # initializing the counter variables #
        total_length = 0
        not_found_length = 0
        # looping through the val sample rows #
        for row in val_dv_reader:
                device_id = row[0]  # first element in the list is device id
                cookie_ids = eval(row[1])  # second element in the list is cookie_ids list
                all_cookie_list = []
                all_cookie_list_list = []
                for ip in device_dict[device_id]:
                        # skip if the ip is not present in the ip_dict #
                        try:
                                cookie_list = ip_dict[ip]
                        except KeyError:
                                continue
                        # skipping those ips where there are more number of cookies associated with it, say more than 30 #
                        if len(cookie_list) > 30:
                                continue
                        # adding the cookie list of current ip to all cookie list #
                        all_cookie_list.extend(cookie_list)
                        all_cookie_list_list.append(cookie_list)
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
                        out_row.extend([ device_id, cookie, cookie_count_dict[cookie], len(device_dict[device_id]), len(cookie_dict[cookie]), cookie_count_dict[cookie]/float(len(device_dict[device_id])), len(cookie_dict[cookie])/float(len(device_dict[device_id])) ])
                        min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip = getMinMaxMean(cookie, all_cookie_list_list)
                        out_row.extend([ min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip ])
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


	print "Getting all rows for test sample based on IP match.."
        test_dv_reader = csv.reader(test_dv_handle)
        test_all_rows_writer = csv.writer(test_all_rows_handle)
        # working on headers #
        test_dv_reader.next()  # skipping the header
        test_all_rows_writer.writerow(['device_id', 'cookie_id', 'cookie_count', 'num_ip_with_device', 'num_ip_with_cookie', 'ratio_cookie_count_by_num_ip_device', 'ratio_num_ip_cookie_by_num_ip_device', 'min_cookie_in_ip', 'max_cookie_in_ip', 'mean_cookie_in_ip', 'DV'])
        # initializing the counter variables #
        total_length = 0
        # looping through the val sample rows #
        for row in test_dv_reader:
                device_id = row[0]  # first element in the list is device id
                all_cookie_list = []
                all_cookie_list_list = []
                for ip in device_dict[device_id]:
                        # skip if the ip is not present in the ip_dict #
                        try:
                                cookie_list = ip_dict[ip]
                        except KeyError:
                                continue
                        # skipping those ips where there are more number of cookies associated with it, say more than 30 #
                        if len(cookie_list) > 30:
                                continue
                        # adding the cookie list of current ip to all cookie list #
                        all_cookie_list.extend(cookie_list)
                        all_cookie_list_list.append(cookie_list)
                # getting the unique cookies from all the ips #
                all_cookie_set = set(all_cookie_list)
                # get the count of occurrance of cookies in form of dict #
                cookie_count_dict = {}
                for cookie in all_cookie_list:
                        cookie_count_dict[cookie] = cookie_count_dict.get(cookie,0) + 1
                # writing to the all rows files for all the cookies identified through ips along with few variables # 
                for cookie in all_cookie_set:
                        out_row = []
                        out_row.extend([ device_id, cookie, cookie_count_dict[cookie], len(device_dict[device_id]), len(cookie_dict[cookie]), cookie_count_dict[cookie]/float(len(device_dict[device_id])), len(cookie_dict[cookie])/float(len(device_dict[device_id])) ])
                        min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip = getMinMaxMean(cookie, all_cookie_list_list)
                        out_row.extend([ min_cookie_in_ip, max_cookie_in_ip, mean_cookie_in_ip ])
                        out_row.append(0)
                        test_all_rows_writer.writerow(out_row)
        print "Total number of cookies in test sample : ",total_length
        print "Number of cookies not captured based on IP address match : ",not_found_length
        # closing the file handlers #
        test_all_rows_handle.close()
        test_dv_handle.close()
