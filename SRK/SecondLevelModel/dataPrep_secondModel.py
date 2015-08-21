import csv
import pandas as pd
import numpy as np

if __name__ == "__main__":
	data_path = "../../Data/"
	cookie_file = data_path + "cookie_all_basic.csv"
	val_preds_file = "val_predictions.csv"
	test_preds_file = "test_predictions.csv"

	print "Reading into pandas df.."
	cookie_drawbridge_df = pd.read_csv(cookie_file, usecols = ["drawbridge_handle","cookie_id"])
	val_preds_df = pd.read_csv(val_preds_file)
	test_preds_df = pd.read_csv(test_preds_file )

	out_header = ['DV', 'cookie_id', 'device_id', 'prediction', 'drawbridge_handle', 'dummy_handle_minusone', 'mean_prediction_handle', 'count_handle', 'diff_from_max_prediction_handle']

	print "Processing val data..."
	out_file = "val_second_level.csv"
	writer = csv.writer(open(out_file,"w"))
	merged_df = pd.merge(val_preds_df, cookie_drawbridge_df, on='cookie_id')
	merged_df_grouped = merged_df.groupby('device_id')
	writer.writerow(out_header)
	counter = 0
	for name, orig_group in merged_df_grouped:
		group = orig_group.copy()
		group["dummy_handle_minusone"] = (group["drawbridge_handle"] == "-1").astype('int')

		"""
		###### Used dataframe groupby operations which is very slow, so switching to manual for loop below ;) ##########
		new_group = group.groupby('drawbridge_handle',as_index=False).agg({'prediction':['mean','count']})
		new_group.columns = ["drawbridge_handle", "mean_prediction_handle", "count_handle"]
		max_pred_handle = np.max(new_group["mean_prediction_handle"])
		new_group['diff_from_max'] = max_pred_handle - new_group["mean_prediction_handle"] 
		merged_group = pd.merge(group, new_group, on='drawbridge_handle')
		assert orig_group.shape[0] == merged_group.shape[0]
		final_df = pd.concat([final_df, merged_group])
		"""

		drawbridge_dict = {}
		for index,row in group.iterrows():
			temp_list = drawbridge_dict.get( row['drawbridge_handle'], [])
			temp_list.append(row['prediction'])
			drawbridge_dict[row['drawbridge_handle']] = temp_list[:]

		mean_count_pred_dict = {}
		max_pred_val = 0
		for key in drawbridge_dict.keys():
				mean_val = np.mean(drawbridge_dict[key])
				mean_count_pred_dict[key] = [ mean_val, np.size(drawbridge_dict[key])]
				if mean_val > max_pred_val:
					max_pred_val = mean_val

		for index,row in group.iterrows():
			handle = row['drawbridge_handle']
			out_row = [row['DV'], row['cookie_id'], row['device_id'], row['prediction'], row['drawbridge_handle'], row['dummy_handle_minusone'], mean_count_pred_dict[handle][0], mean_count_pred_dict[handle][1], max_pred_val-mean_count_pred_dict[handle][0]]
			assert len(out_header) == len(out_row)
			writer.writerow(out_row)	
		
		
	print "Processing test data..."
        out_file = "test_second_level.csv"
        writer = csv.writer(open(out_file,"w"))
        merged_df = pd.merge(test_preds_df, cookie_drawbridge_df, on='cookie_id')
        merged_df_grouped = merged_df.groupby('device_id')
        writer.writerow(out_header)
        counter = 0
        for name, orig_group in merged_df_grouped:
                group = orig_group.copy()
                group["dummy_handle_minusone"] = (group["drawbridge_handle"] == "-1").astype('int')

                """
                ###### Used dataframe groupby operations which is very slow, so switching to manual for loop below ;) ##########
                new_group = group.groupby('drawbridge_handle',as_index=False).agg({'prediction':['mean','count']})
                new_group.columns = ["drawbridge_handle", "mean_prediction_handle", "count_handle"]
                max_pred_handle = np.max(new_group["mean_prediction_handle"])
                new_group['diff_from_max'] = max_pred_handle - new_group["mean_prediction_handle"] 
                merged_group = pd.merge(group, new_group, on='drawbridge_handle')
                assert orig_group.shape[0] == merged_group.shape[0]
                final_df = pd.concat([final_df, merged_group])
                """

                drawbridge_dict = {}
                for index,row in group.iterrows():
                        temp_list = drawbridge_dict.get( row['drawbridge_handle'], [])
                        temp_list.append(row['prediction'])
                        drawbridge_dict[row['drawbridge_handle']] = temp_list[:]

                mean_count_pred_dict = {}
                max_pred_val = 0
                for key in drawbridge_dict.keys():
                                mean_val = np.mean(drawbridge_dict[key])
                                mean_count_pred_dict[key] = [ mean_val, np.size(drawbridge_dict[key])]
                                if mean_val > max_pred_val:
                                        max_pred_val = mean_val

                for index,row in group.iterrows():
                        handle = row['drawbridge_handle']
                        out_row = [row['DV'], row['cookie_id'], row['device_id'], row['prediction'], row['drawbridge_handle'], row['dummy_handle_minusone'], mean_count_pred_dict[handle][0], mean_count_pred_dict[handle][1], max_pred_val-mean_count_pred_dict[handle][0]]
                        assert len(out_header) == len(out_row)
                        writer.writerow(out_row)	
