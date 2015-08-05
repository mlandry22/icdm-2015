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

	ip_agg_dict = {}
	for row in reader:
		ip_agg_dict[int(row[0][2:])] = row[1:]

	return ip_agg_dict

def writeVars(in_handle, out_handle, ip_agg_dict):
	reader = csv.DictReader(in_handle)
	writer = csv.writer(out_handle)

	header = ["device_id", "cookie_id", "common_ip_device_freq_sum", "common_ip_device_c1_sum", "common_ip_device_c2_sum", "common_ip_device_c3_sum", "common_ip_device_c4_sum", "common_ip_device_c5_sum", "common_ip_cookie_freq_sum", "common_ip_cookie_c1_sum", "common_ip_cookie_c2_sum", "common_ip_cookie_c3_sum", "common_ip_cookie_c4_sum", "common_ip_cookie_c5_sum", "common_ip_device_freq_avg", "common_ip_device_c1_avg", "common_ip_device_c2_avg", "common_ip_device_c3_avg", "common_ip_device_c4_avg", "common_ip_device_c5_avg", "common_ip_cookie_freq_avg", "common_ip_cookie_c1_avg", "common_ip_cookie_c2_avg", "common_ip_cookie_c3_avg", "common_ip_cookie_c4_avg", "common_ip_cookie_c5_avg", "device_freq_common_ip_by_all_ip", "device_c1_common_ip_by_all_ip", "device_c2_common_ip_by_all_ip", "device_c3_common_ip_by_all_ip", "device_c4_common_ip_by_all_ip", "device_c5_common_ip_by_all_ip", "cookie_freq_common_ip_by_all_ip", "cookie_c1_common_ip_by_all_ip", "cookie_c2_common_ip_by_all_ip", "cookie_c3_common_ip_by_all_ip", "cookie_c4_common_ip_by_all_ip", "cookie_c5_common_ip_by_all_ip", "cell_ip_sum", "cell_ip_avg", "ip_c0_sum", "ip_c0_avg", "ip_c1_sum", "ip_c1_avg", "ip_c2_sum", "ip_c2_avg", "ip_freq_sum", "ip_freq_avg", "cell_ip_rate_device", "cell_ip_rate_cookie"]
	writer.writerow(header)

	counter = 0
	for row in reader:
		device_id = row["device_id"]
		cookie_id = row["cookie_id"]
		out_row = [device_id, cookie_id]
		device_ip_list = eval(row["device_ip_list"])
		cookie_ip_list = eval(row["cookie_ip_list"])

		device_ips = set([ip_list[0] for ip_list in device_ip_list])
		cookie_ips = set([ip_list[0] for ip_list in cookie_ip_list])
		common_ips = list(device_ips.intersection(cookie_ips))

		device_ip_dict = {}
		for ip_list in device_ip_list:
			device_ip_dict[ip_list[0]] = ip_list[1:]

		cookie_ip_dict = {}
		for ip_list in cookie_ip_list:
                        cookie_ip_dict[ip_list[0]] = ip_list[1:]

		# sum and average of count of freq and other anonymous features in the common ips #
		device_freq_sum = 0.
		device_c1_sum = 0.
		device_c2_sum = 0.
		device_c3_sum = 0.
		device_c4_sum = 0.
		device_c5_sum = 0.
		cookie_freq_sum = 0.
                cookie_c1_sum = 0.
                cookie_c2_sum = 0.
                cookie_c3_sum = 0.
                cookie_c4_sum = 0.
                cookie_c5_sum = 0.
		cell_ip_sum = 0.
		ip_c0_sum = 0.
		ip_c1_sum = 0.
		ip_c2_sum = 0.
		ip_freq_sum = 0.
		for common_ip in common_ips:
			device_freq_sum += int(device_ip_dict[common_ip][0])
			device_c1_sum += int(device_ip_dict[common_ip][1])
			device_c2_sum += int(device_ip_dict[common_ip][2])
			device_c3_sum += int(device_ip_dict[common_ip][3])
			device_c4_sum += int(device_ip_dict[common_ip][4])
			device_c5_sum += int(device_ip_dict[common_ip][5])
                        cookie_freq_sum += int(cookie_ip_dict[common_ip][0])
                        cookie_c1_sum += int(cookie_ip_dict[common_ip][1])
                        cookie_c2_sum += int(cookie_ip_dict[common_ip][2])
                        cookie_c3_sum += int(cookie_ip_dict[common_ip][3])
                        cookie_c4_sum += int(cookie_ip_dict[common_ip][4])
                        cookie_c5_sum += int(cookie_ip_dict[common_ip][5])
			if ip_agg_dict.has_key(common_ip):
				cell_ip_sum += int(ip_agg_dict[common_ip][0])
				ip_freq_sum += ( int(device_ip_dict[common_ip][0]) + int(cookie_ip_dict[common_ip][0]) ) / float(ip_agg_dict[common_ip][1])
				ip_c0_sum += int(ip_agg_dict[common_ip][2])
				ip_c1_sum += int(ip_agg_dict[common_ip][3])
				ip_c2_sum += int(ip_agg_dict[common_ip][4])
                device_freq_avg = round( device_freq_sum / float(len(common_ips)) ,5)
                device_c1_avg = round( device_c1_sum / float(len(common_ips)) ,5)
                device_c2_avg = round( device_c2_sum / float(len(common_ips)) ,5)
                device_c3_avg = round( device_c3_sum / float(len(common_ips)) ,5)
                device_c4_avg = round( device_c4_sum / float(len(common_ips)) ,5)
                device_c5_avg = round( device_c5_sum / float(len(common_ips)) ,5)
                cookie_freq_avg = round( cookie_freq_sum / float(len(common_ips)) ,5)
                cookie_c1_avg = round( cookie_c1_sum / float(len(common_ips)) ,5)
                cookie_c2_avg = round( cookie_c2_sum / float(len(common_ips)) ,5)
                cookie_c3_avg = round( cookie_c3_sum / float(len(common_ips)) ,5)
                cookie_c4_avg = round( cookie_c4_sum / float(len(common_ips)) ,5)
                cookie_c5_avg = round( cookie_c5_sum / float(len(common_ips)) ,5)
		out_row.extend( [device_freq_sum, device_c1_sum, device_c2_sum, device_c3_sum, device_c4_sum, device_c5_sum, cookie_freq_sum, cookie_c1_sum, cookie_c2_sum, cookie_c3_sum, cookie_c4_sum, cookie_c5_sum, device_freq_avg, device_c1_avg, device_c2_avg, device_c3_avg, device_c4_avg, device_c5_avg, cookie_freq_avg, cookie_c1_avg, cookie_c2_avg, cookie_c3_avg, cookie_c4_avg, cookie_c5_avg] )


		# get the rate of freq and other anonymous features in common ips by all ips #
                device_freq_all_ip_sum = 0.
                device_c1_all_ip_sum = 0.
                device_c2_all_ip_sum = 0.
                device_c3_all_ip_sum = 0.
                device_c4_all_ip_sum = 0.
                device_c5_all_ip_sum = 0.
		device_cell_ip_sum = 0.
		for device_ip in device_ips:
			device_freq_all_ip_sum += int(device_ip_dict[device_ip][0])
                        device_c1_all_ip_sum += int(device_ip_dict[device_ip][1])
                        device_c2_all_ip_sum += int(device_ip_dict[device_ip][2])
                        device_c3_all_ip_sum += int(device_ip_dict[device_ip][3])
                        device_c4_all_ip_sum += int(device_ip_dict[device_ip][4])
                        device_c5_all_ip_sum += int(device_ip_dict[device_ip][5])
			if ip_agg_dict.has_key(device_ip):
				device_cell_ip_sum += int(ip_agg_dict[device_ip][0])
		device_freq_common_ip_by_all_ip = round( device_freq_sum / max(device_freq_all_ip_sum,1) ,5)
		device_c1_common_ip_by_all_ip = round( device_c1_sum / max(device_c1_all_ip_sum,1) ,5)
		device_c2_common_ip_by_all_ip = round( device_c2_sum / max(device_c2_all_ip_sum,1) ,5)
		device_c3_common_ip_by_all_ip = round( device_c3_sum / max(device_c3_all_ip_sum,1) ,5)
		device_c4_common_ip_by_all_ip = round( device_c4_sum / max(device_c4_all_ip_sum,1) ,5)
		device_c5_common_ip_by_all_ip = round( device_c5_sum / max(device_c5_all_ip_sum,1) ,5)
		out_row.extend( [device_freq_common_ip_by_all_ip, device_c1_common_ip_by_all_ip, device_c2_common_ip_by_all_ip, device_c3_common_ip_by_all_ip, device_c4_common_ip_by_all_ip, device_c5_common_ip_by_all_ip] )

		cookie_freq_all_ip_sum = 0.
                cookie_c1_all_ip_sum = 0.
                cookie_c2_all_ip_sum = 0.
                cookie_c3_all_ip_sum = 0.
                cookie_c4_all_ip_sum = 0.
                cookie_c5_all_ip_sum = 0.
		cookie_cell_ip_sum = 0.
                for cookie_ip in cookie_ips:
                        cookie_freq_all_ip_sum += int(cookie_ip_dict[cookie_ip][0])
                        cookie_c1_all_ip_sum += int(cookie_ip_dict[cookie_ip][1])
                        cookie_c2_all_ip_sum += int(cookie_ip_dict[cookie_ip][2])
                        cookie_c3_all_ip_sum += int(cookie_ip_dict[cookie_ip][3])
                        cookie_c4_all_ip_sum += int(cookie_ip_dict[cookie_ip][4])
                        cookie_c5_all_ip_sum += int(cookie_ip_dict[cookie_ip][5])
			if ip_agg_dict.has_key(cookie_ip):
                                cookie_cell_ip_sum += int(ip_agg_dict[cookie_ip][0])
                cookie_freq_common_ip_by_all_ip = round( cookie_freq_sum / max(cookie_freq_all_ip_sum,1) ,5)
                cookie_c1_common_ip_by_all_ip = round( cookie_c1_sum / max(cookie_c1_all_ip_sum,1) ,5)
                cookie_c2_common_ip_by_all_ip = round( cookie_c2_sum / max(cookie_c2_all_ip_sum,1) ,5)
                cookie_c3_common_ip_by_all_ip = round( cookie_c3_sum / max(cookie_c3_all_ip_sum,1) ,5)
                cookie_c4_common_ip_by_all_ip = round( cookie_c4_sum / max(cookie_c4_all_ip_sum,1) ,5)
                cookie_c5_common_ip_by_all_ip = round( cookie_c5_sum / max(cookie_c5_all_ip_sum,1) ,5)
                out_row.extend( [cookie_freq_common_ip_by_all_ip, cookie_c1_common_ip_by_all_ip, cookie_c2_common_ip_by_all_ip, cookie_c3_common_ip_by_all_ip, cookie_c4_common_ip_by_all_ip, cookie_c5_common_ip_by_all_ip] )


		# get variables from ip aggr table #
		cell_ip_avg = round( cell_ip_sum / float(len(common_ips)), 5)
                ip_c0_avg = round( ip_c0_sum / float(len(common_ips)), 5)
                ip_c1_avg = round( ip_c1_sum/ float(len(common_ips)), 5)
                ip_c2_avg = round( ip_c2_sum / float(len(common_ips)), 5)
                ip_freq_avg = round( ip_freq_sum / float(len(common_ips)), 5)
		cell_ip_rate_device = round( cell_ip_sum / max(device_cell_ip_sum,1), 5)
		cell_ip_rate_cookie = round( cell_ip_sum / max(cookie_cell_ip_sum,1), 5)
		out_row.extend( [cell_ip_sum, cell_ip_avg, ip_c0_sum, ip_c0_avg, ip_c1_sum, ip_c1_avg, ip_c2_sum, ip_c2_avg, round(ip_freq_sum,5), ip_freq_avg, cell_ip_rate_device, cell_ip_rate_cookie] )

		assert len(header) == len(out_row)
		writer.writerow(out_row)

		counter += 1
		if counter % 100000 == 0:
			print "Processed : ", counter

	# closing the file handlers #
	in_handle.close()
	out_handle.close()


if __name__ == "__main__":
	# path of the input files #
	data_path = "../../Data/"

	# specify the input files #
	ip_agg_file = data_path + "ipagg_all.csv"
	dev_ip_vars_file = data_path + "dev_ip_vars_inter.csv"
	val_ip_vars_file = data_path + "val_ip_vars_inter.csv"
	test_ip_vars_file = data_path + "test_ip_vars_inter.csv"
	final_dev_ip_vars_file = data_path + "dev_ip_vars.csv"
        final_val_ip_vars_file = data_path + "val_ip_vars.csv"
        final_test_ip_vars_file = data_path + "test_ip_vars.csv"

	# creating a handle for each #
	dev_ip_vars_handle = open(dev_ip_vars_file)
	val_ip_vars_handle = open(val_ip_vars_file)
	test_ip_vars_handle = open(test_ip_vars_file)
	ip_agg_handle = open(ip_agg_file)

	print "Getting IP Agg dict.."
	ip_agg_dict = getIPAggDict(ip_agg_handle)
	#ip_agg_dict = {}

	###############################         DEV SAMPLE          ###########################################
	print "Getting variables related to IP on Dev Sample.."
	final_dev_ip_vars_handle = open(final_dev_ip_vars_file,"w")
	writeVars(dev_ip_vars_handle, final_dev_ip_vars_handle, ip_agg_dict)

	
	print "Getting variables related to IP on Val Sample.."
	final_val_ip_vars_handle = open(final_val_ip_vars_file,"w")
	writeVars(val_ip_vars_handle, final_val_ip_vars_handle, ip_agg_dict)


	print "Getting variables related to IP on Test Sample.."
	final_test_ip_vars_handle = open(final_test_ip_vars_file,"w")
	writeVars(test_ip_vars_handle, final_test_ip_vars_handle, ip_agg_dict)
