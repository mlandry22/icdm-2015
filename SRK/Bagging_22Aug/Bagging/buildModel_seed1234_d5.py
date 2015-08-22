"""
This code is to build the models from the given input file and  store the predcitions in a csv file.
"""
import sys
import csv
import numpy as np
import pandas as pd
from sklearn import ensemble
from sklearn.metrics import roc_auc_score
sys.path.append("/home/sudalai/Softwares/xgboost-master/wrapper/")
import xgboost as xgb


if __name__ == "__main__":
	# input file names #
	data_path = "./NewData/"
	dev_file = data_path + "dev_final_vars_seed1234.csv"
	val_file = data_path + "val_final_vars.csv"
	test_file = data_path + "test_final_vars.csv"

	# reading the data from files into pandas dataframe #
	print "Preparing dev data.."
	dev_data = pd.read_csv(dev_file)

	print "Dev shape : ",dev_data.shape
	print "Sum of Dev DV : ",sum(dev_data['DV'])

	# data preparation #
	dev_X = np.array(dev_data)[:,2:-1]
	dev_y = np.array(dev_data['DV'])
	dev_device_id = np.array( dev_data['device_id'] )
	dev_cookie_id = np.array( dev_data['cookie_id'] )
	xgtrain = xgb.DMatrix(dev_X, label=dev_y)

	# clean up RAM #
	del dev_data
	del dev_X
	import gc
	gc.collect()

	print "Preparing Val data.."
	val_data = pd.read_csv(val_file)
	val_y = np.array(val_data['DV'])
	val_device_id = np.array( val_data['device_id'] )
	val_cookie_id = np.array( val_data['cookie_id'] )
	#val_X = np.array(val_data)[:,2:-1]
        xgtest = xgb.DMatrix(np.array(val_data)[:,2:-1], label=val_y)

	del val_data
	gc.collect()


	################## XGBoost ###############
	print "Preparing data for XGB.."
	params = {}
        params["objective"] = "binary:logistic"
        params["eta"] = 0.15
        params["min_child_weight"] = 30
        params["subsample"] = 0.7
        params["colsample_bytree"] = 0.6
        params["scale_pos_weight"] = 0.8
        params["silent"] = 1
        params["max_depth"] = 5
        params["max_delta_step"]=2
        params["seed"] = 0
	params['eval_metric'] = "auc"

        plst = list(params.items())
	watchlist = [ (xgtrain,'train'), (xgtest, 'test') ]

	print "Running model.."
	num_rounds = 550
        model = xgb.train(plst, xgtrain, num_rounds, watchlist)
	pred_dev_y = model.predict(xgtrain)
	pred_val_y = model.predict(xgtest)

	del xgtrain
	del xgtest
	gc.collect()

	# AUC score on dev and val sample #
	print "Dev AUC : ", roc_auc_score(dev_y, pred_dev_y)
	print "Val AUC : ", roc_auc_score(val_y, pred_val_y)

	
	# saving the predcitions into csv file #
	print "Saving predctions.."
	dev_pred_df = pd.DataFrame({'device_id':dev_device_id, 'cookie_id':dev_cookie_id, 'prediction':pred_dev_y, 'DV':dev_y})
	val_pred_df = pd.DataFrame({'device_id':val_device_id, 'cookie_id':val_cookie_id, 'prediction':pred_val_y, 'DV':val_y})
	dev_pred_df.to_csv("dev_predictions_seed1234_d5.csv", index=False)
	val_pred_df.to_csv("val_predictions_seed1234_d5.csv", index=False)

	# cleaning up #
	del dev_pred_df
	del val_pred_df
	gc.collect()

	import gc
	gc.collect()
	
	
	#import sys
	#print "Exiting after computing CV and saving it.."
	#sys.exit()

	## Working on test data set ##
	"""
	print "Working on test file.."
	test_data = pd.read_csv(test_file)
	#test_X = np.array(test_data)[:,2:-1]
	xgtest = xgb.DMatrix(np.array(test_data)[:,2:-1])
	test_y = np.array(test_data['DV'])
	test_device_id = np.array(test_data['device_id'])
	test_cookie_id = np.array(test_data['cookie_id'])
	del test_data
	gc.collect()
	print "Making predictions.."
	pred_test_y = model.predict(xgtest)
	test_pred_df = pd.DataFrame({'device_id':test_device_id, 'cookie_id':test_cookie_id, 'prediction':pred_test_y, 'DV':test_y})
	test_pred_df.to_csv("test_predictions.csv", index=False)
	"""


	
	test_writer = csv.writer(open("test_predictions_seed1234_d5.csv", "w"))
        test_writer.writerow(["device_id", "cookie_id", "prediction", "DV"])
        full_test = pd.read_csv(test_file, chunksize=500000)
        for test in full_test:
                print "Reading new chunk..."
                xgtest = xgb.DMatrix(test.iloc[:,2:-1])
                preds = model.predict(xgtest)

                for row_no in xrange(test.shape[0]):
                        test_writer.writerow([test["device_id"][row_no], test["cookie_id"][row_no], preds[row_no], test['DV'][row_no]])
