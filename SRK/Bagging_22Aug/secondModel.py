import sys
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
sys.path.append("/home/sudalai/Softwares/xgboost-master/wrapper/")
import xgboost as xgb

if __name__ == "__main__":
	val_file = "val_second_level.csv"
	test_file = "test_second_level.csv"

	val = pd.read_csv(val_file)
	val_dv = np.array(val["DV"])
	device_id_arr = np.array(val["device_id"])
	cookie_id_arr = np.array(val["cookie_id"])

	val = np.array(val.iloc[:,[3,5,6,7,8,9,10,11,12]])
	print val.shape, val_dv.shape

	develop_X = val[:1182988,:]
	develop_y = val_dv[:1182988]

	validate_X = val[1182988:,:]
	validate_y = val_dv[1182988:]

	print develop_X.shape, validate_X.shape

	################## XGBoost ###############
        print "Preparing data for XGB.."
        params = {}
        params["objective"] = "binary:logistic"
        params["eta"] = 0.02
        params["min_child_weight"] = 30
        params["subsample"] = 0.7
        params["colsample_bytree"] = 0.6
        params["scale_pos_weight"] = 0.8
        params["silent"] = 1
        params["max_depth"] = 5
        params["max_delta_step"]=2
        params["seed"] = 0
        params['eval_metric'] = "auc"

	xgtrain = xgb.DMatrix(develop_X, label=develop_y)
	xgtest = xgb.DMatrix(validate_X, label=validate_y)
        plst = list(params.items())
        watchlist = [ (xgtrain,'train'), (xgtest, 'test') ]

        print "Running model.."
        num_rounds = 440
        model = xgb.train(plst, xgtrain, num_rounds, watchlist)
        pred_dev_y = model.predict(xgtrain)
        pred_val_y = model.predict(xgtest)

        del xgtrain
        del xgtest
	import gc
        gc.collect()

	#import sys
	#sys.exit()


        # AUC score on dev and val sample #
	print develop_y.shape, type(develop_y), develop_y[:5]
	print pred_dev_y.shape, type(pred_dev_y), np.min(pred_dev_y), np.max(pred_dev_y)
        print "Dev AUC : ", roc_auc_score(np.array(develop_y), pred_dev_y)
        print "Val AUC : ", roc_auc_score(np.array(validate_y), pred_val_y)

	print "Saving predctions.."
        dev_pred_df = pd.DataFrame({'device_id':device_id_arr[:1182988], 'cookie_id':cookie_id_arr[:1182988], 'prediction':pred_dev_y, 'DV':develop_y})
        val_pred_df = pd.DataFrame({'device_id':device_id_arr[1182988:], 'cookie_id':cookie_id_arr[1182988:], 'prediction':pred_val_y, 'DV':validate_y})
        dev_pred_df.to_csv("dev_predictions_m2.csv", index=False)
        val_pred_df.to_csv("val_predictions_m2.csv", index=False)

	print "Working on the test file.."
	test = pd.read_csv(test_file)
        test_dv = np.array(test["DV"])
        device_id_arr = np.array(test["device_id"])
        cookie_id_arr = np.array(test["cookie_id"])

	test = np.array(test.iloc[:,[3,5,6,7,8,9,10,11,12]])
	xgtest = xgb.DMatrix(test)
	pred_test_y = model.predict(xgtest)
	test_pred_df = pd.DataFrame({'device_id':device_id_arr, 'cookie_id':cookie_id_arr, 'prediction':pred_test_y, 'DV':test_dv})
	test_pred_df.to_csv("test_predictions_m2.csv", index=False)
