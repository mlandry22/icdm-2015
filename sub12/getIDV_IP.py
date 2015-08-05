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
	cookie_dict = {}

        counter = 0                        # counter to manage the progress
        for row in reader:
                counter += 1

                # extracting ip address alone from the given input and store it in a list #
                ip_all_str = ','.join(row[2:])
                ip_list = []
                ip_all_list = ip_all_str.replace("{","").replace("}","").replace("),("," ").replace("(","").replace(")","").split(" ")     # formatting 
                for val in ip_all_list:
			val = val.split(",")
			out_list = []
			for ind, var_val in enumerate(val):
				if ind != 0:
					out_list.append(int(var_val))
				else:
					out_list.append(int(var_val[2:])) 
                        ip_list.append(out_list)
		#print ip_all_list

                # if device, write to device dict, else write to ip dict #
                if row[1] == '0':
                        device_dict[row[0]] = ip_list
                elif row[1] == '1':
			cookie_dict[row[0]] = ip_list
                else:
                        print "Device or Cookie has unacceptable value.. Value : ", row[1]
                        raise
		
                # printing the progress #
                if counter % 100000 == 0:
                        print "Processed : ", counter

        return device_dict, cookie_dict

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
			
def getIPAggDict(ip_agg_handle):
	reader = csv.reader(ip_agg_handle)
	reader.next()

	ip_agg_list = []
	for row in reader:
		ip_agg_list.append(row)

	return ip_agg_list

def writeVars(in_handle, out_handle, device_dict, cookie_dict):
	reader = csv.DictReader(in_handle)
	writer = csv.writer(out_handle)

	writer.writerow(["device_id", "cookie_id", "device_ip_list", "cookie_ip_list"])

	for row in reader:
		device_id = row["device_id"]
		cookie_id = row["cookie_id"]
		try:
			device_ip_list = device_dict[device_id]
		except:
			device_ip_list = []
		try:
			cookie_ip_list = cookie_dict[cookie_id]
		except:
			cookie_ip_list = []

		writer.writerow([device_id, cookie_id, device_ip_list, cookie_ip_list])

	# closing the file handlers #
	in_handle.close()
	out_handle.close()


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
	ip_agg_file = data_path + "ipagg_all.csv"
	dev_ip_vars_file = data_path + "dev_ip_vars_inter.csv"
	val_ip_vars_file = data_path + "val_ip_vars_inter.csv"
	test_ip_vars_file = data_path + "test_ip_vars_inter.csv"

	# creating a handle for each #
	dev_dv_handle = open(dev_dv_file)
	dev_all_rows_handle = open(dev_all_rows_file)
	val_dv_handle = open(val_dv_file)
	val_all_rows_handle = open(val_all_rows_file)
	id_all_ip_handle = open(id_all_ip_file)
	test_dv_handle = open(sample_sub_file)
	test_all_rows_handle = open(test_all_rows_file)
	ip_agg_handle = open(ip_agg_file)

	
	print "Getting device and IP dict.."
        device_dict, cookie_dict = getIPDict(id_all_ip_handle)
	id_all_ip_handle.close()


	shared_ip_cutoff = 30 
	###############################         DEV SAMPLE          ###########################################
	print "Getting variables related to IP on Dev Sample.."
	dev_ip_vars_handle = open(dev_ip_vars_file,"w")
	writeVars(dev_all_rows_handle, dev_ip_vars_handle, device_dict, cookie_dict)
	print "Getting variables related to IP on Val Sample.."
	val_ip_vars_handle = open(val_ip_vars_file,"w")
	writeVars(val_all_rows_handle, val_ip_vars_handle, device_dict, cookie_dict)
	print "Getting variables related to IP on Test Sample.."
	test_ip_vars_handle = open(test_ip_vars_file,"w")
	writeVars(test_all_rows_handle, test_ip_vars_handle, device_dict, cookie_dict)
