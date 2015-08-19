import sys
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
sys.path.append("/home/sudalai/Softwares/xgboost-master/wrapper/")
import xgboost as xgb

if __name__ == "__main__":
	data_path = "../../Data/"
	val_file1 = data_path + "val_final_vars.csv"
	val_file2 = "mod_val_preds.csv"

	val1 = np.array(pd.read_csv(val_file1))
	val2 = np.array(pd.read_csv(val_file2))[:,3:]

	print val1.shape
	print val2.shape

	val_dv = np.array(val1[:,-1]).ravel()
	val1 = val1[:,:-1]
	val = np.hstack([val1, val2])

	del val1
	del val2
	import gc
	gc.collect()

	develop_X = val[:1182988,2:]
	develop_y = val_dv[:1182988]

	validate_X = val[1182988:,2:]
	validate_y = val_dv[1182988:]

	print develop_X.shape, validate_X.shape

	################## XGBoost ###############
        print "Preparing data for XGB.."
        params = {}
        params["objective"] = "binary:logistic"
        params["eta"] = 0.15
        params["min_child_weight"] = 10
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
        num_rounds = 100
        model = xgb.train(plst, xgtrain, num_rounds, watchlist)
        pred_dev_y = model.predict(xgtrain)
        pred_val_y = model.predict(xgtest)

        del xgtrain
        del xgtest
        gc.collect()

        # AUC score on dev and val sample #
	print develop_y.shape, type(develop_y), develop_y[:5]
	print pred_dev_y.shape, type(pred_dev_y), np.min(pred_dev_y), np.max(pred_dev_y)
        #print "Dev AUC : ", roc_auc_score(np.array(develop_y), pred_dev_y)
        #print "Val AUC : ", roc_auc_score(np.array(validate_y), pred_val_y)

	print "Saving predctions.."
        dev_pred_df = pd.DataFrame({'device_id':val[:1182988,0], 'cookie_id':val[:1182988,1], 'prediction':pred_dev_y, 'DV':develop_y})
        val_pred_df = pd.DataFrame({'device_id':val[1182988:,0], 'cookie_id':val[1182988:,1], 'prediction':pred_val_y, 'DV':validate_y})
        dev_pred_df.to_csv("dev_predictions_m2.csv", index=False)
        val_pred_df.to_csv("val_predictions_m2.csv", index=False)
