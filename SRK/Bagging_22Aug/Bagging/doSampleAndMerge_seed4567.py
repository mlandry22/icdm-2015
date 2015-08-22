import csv
import random

def sampleAndMerge(in_file1, in_file2, out_file, sample=None):
	in_handle1 = open(in_file1)
	in_handle2 = open(in_file2)
	out_handle = open(out_file,"w")

	reader1 = csv.reader(in_handle1)
	reader2 = csv.reader(in_handle2)
	writer = csv.writer(out_handle)

	header = reader1.next()[:-1]
	header.extend((reader2.next())[2:])
	header.append("DV")
	header_len = len(header)
	writer.writerow(header)

	random.seed(4567)
	for row1 in reader1:
		row2 = reader2.next()
		assert row1[0] == row2[0]
		assert row1[1] == row2[1]

		if int(row1[-1]) == 1:
			out_row = row1[:-1] + row2[2:] + [row1[-1]]
		else:
			if sample:
				rand_no = random.randint(1,sample)
				if rand_no != 1:
					continue
			out_row = row1[:-1] + row2[2:] + [row1[-1]]

		assert header_len == len(out_row)
		writer.writerow(out_row)
		#break
	
	in_handle1.close()
	in_handle2.close()
	out_handle.close()
				

if __name__ == "__main__":
	data_path = "../../Data/"
	out_path = "./NewData/"

	print "Dev..."	
	in_file1 = data_path + "dev_all_rows.csv"
	in_file2 = data_path + "dev_ip_vars.csv"
	out_file = out_path + "dev_final_vars_seed4567.csv"
	sampleAndMerge(in_file1, in_file2, out_file, sample=6)

	"""	
	print "Val..."
	in_file1 = data_path + "val_all_rows.csv"
        in_file2 = data_path + "val_ip_vars.csv"
        out_file = out_path + "val_final_vars.csv"
        sampleAndMerge(in_file1, in_file2, out_file)
	
	print "Test..."
	in_file1 = data_path + "test_all_rows.csv"
        in_file2 = data_path + "test_ip_vars.csv"
        out_file = out_path + "test_final_vars.csv"
        sampleAndMerge(in_file1, in_file2, out_file)
	"""
