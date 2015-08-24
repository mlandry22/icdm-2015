"""
This code is to build the models from the given input file and  store the predcitions in a csv file.
"""
import sys
import numpy as np
import pandas as pd
from sklearn import ensemble
from sklearn.metrics import roc_auc_score
sys.path.append("/home/sudalai/Softwares/xgboost-master/wrapper/")
import xgboost as xgb


if __name__ == "__main__":
	# input file names #
	data_path = "../../Data/"
	dev_file = data_path + "dev_all_rows.csv"
	val_file = data_path + "val_all_rows.csv"
	test_file = data_path + "test_all_rows.csv"

	# reading the data from files into pandas dataframe #
	dev_data = pd.read_csv(dev_file)

	print "Dev shape : ",dev_data.shape
	print "Sum of Dev DV : ",sum(dev_data['DV'])

	# data preparation #
	dev_X = np.array(dev_data)[:,2:-1]
	dev_y = np.array(dev_data['DV'])
	dev_device_id = np.array( dev_data['device_id'] )
	dev_cookie_id = np.array( dev_data['cookie_id'] )

	# clean up RAM #
	del dev_data
	import gc
	gc.collect()

	val_data = pd.read_csv(val_file)
	val_X = np.array(val_data)[:,2:-1]
	val_y = np.array(val_data['DV'])
	val_device_id = np.array( val_data['device_id'] )
	val_cookie_id = np.array( val_data['cookie_id'] )

	del val_data
	gc.collect()


	################## XGBoost ###############
	print "Preparing data for XGB.."
	params = {}
        params["objective"] = "binary:logistic"
        params["eta"] = 0.02
        params["min_child_weight"] = 10
        params["subsample"] = 0.7
        params["colsample_bytree"] = 0.6
        params["scale_pos_weight"] = 0.8
        params["silent"] = 1
        params["max_depth"] = 8
        params["max_delta_step"]=2
        params["seed"] = 0
	params['eval_metric'] = "auc"

        plst = list(params.items())

        xgtrain = xgb.DMatrix(dev_X, label=dev_y)
        xgtest = xgb.DMatrix(val_X, label=val_y)
	watchlist = [ (xgtrain,'train'), (xgtest, 'test') ]

	del dev_X
	del val_X
	gc.collect()

	print "Running model.."
	num_rounds = 1000
        model = xgb.train(plst, xgtrain, num_rounds, watchlist)
	pred_dev_y = model.predict(xgtrain)
	pred_val_y = model.predict(xgtest)

	del xgtrain
	del xgtest
	gc.collect()

	# AUC score on dev and val sample #
	print "Dev AUC : ", roc_auc_score(dev_y, pred_dev_y)
	print "Val AUC : ", roc_auc_score(val_y, pred_val_y)

	#import sys
	#sys.exit()
	
	# saving the predcitions into csv file #
	print "Saving predctions.."
	dev_pred_df = pd.DataFrame({'device_id':dev_device_id, 'cookie_id':dev_cookie_id, 'prediction':pred_dev_y, 'DV':dev_y})
	val_pred_df = pd.DataFrame({'device_id':val_device_id, 'cookie_id':val_cookie_id, 'prediction':pred_val_y, 'DV':val_y})
	dev_pred_df.to_csv("dev_predictions.csv", index=False)
	val_pred_df.to_csv("val_predictions.csv", index=False)

	# cleaning up #
	del dev_pred_df
	del val_pred_df
	gc.collect()

	import gc
	gc.collect()
	

	## Working on test data set ##
	print "Working on test file.."
	test_data = pd.read_csv(test_file)
	test_X = np.array(test_data)[:,2:-1]
	test_y = np.array(test_data['DV'])
	xgtest = xgb.DMatrix(test_X)
	del test_X
	test_device_id = np.array(test_data['device_id'])
	test_cookie_id = np.array(test_data['cookie_id'])
	del test_data
	gc.collect()
	print "Making predictions.."
	pred_test_y = model.predict(xgtest)
	test_pred_df = pd.DataFrame({'device_id':test_device_id, 'cookie_id':test_cookie_id, 'prediction':pred_test_y, 'DV':test_y})
	test_pred_df.to_csv("test_predictions.csv", index=False)
