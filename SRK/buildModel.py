import numpy as np
import pandas as pd
from sklearn import ensemble
from sklearn.metrics import roc_auc_score

if __name__ == "__main__":
	# input file names #
	data_path = "../../Data/"
	dev_file = data_path + "dev_all_rows.csv"
	val_file = data_path + "val_all_rows.csv"
	test_file = data_path + "test_all_rows.csv"

	# reading the data from files into pandas dataframe #
	dev_data = pd.read_csv(dev_file)
	val_data = pd.read_csv(val_file)

	print "Dev, Val shape : ",dev_data.shape, val_data.shape
	print "Sum of Dev and Val DV : ",sum(dev_data['DV']), sum(val_data['DV'])

	dev_X = np.array(dev_data)[:,2:-1]
	val_X = np.array(val_data)[:,2:-1]
	dev_y = np.array(dev_data['DV'])
	val_y = np.array(val_data['DV'])
	dev_device_id = np.array( dev_data['device_id'] )
	val_device_id = np.array( val_data['device_id'] )
	dev_cookie_id = np.array( dev_data['cookie_id'] )
	val_cookie_id = np.array( val_data['cookie_id'] )

	del dev_data
	del val_data
	import gc
	gc.collect()


	clf = ensemble.RandomForestClassifier(n_estimators=50, max_depth=10, min_samples_leaf=10, n_jobs=3, random_state=0)
	clf.fit(dev_X, dev_y)
	pred_dev_y = clf.predict_proba(dev_X)[:,1]
	pred_val_y = clf.predict_proba(val_X)[:,1]

	del dev_X
	del val_X
	gc.collect()

	print "Dev AUC : ", roc_auc_score(dev_y, pred_dev_y)
	print "Val AUC : ", roc_auc_score(val_y, pred_val_y)

	dev_pred_df = pd.DataFrame({'device_id':dev_device_id, 'cookie_id':dev_cookie_id, 'prediction':pred_dev_y, 'DV':dev_y})
	val_pred_df = pd.DataFrame({'device_id':val_device_id, 'cookie_id':val_cookie_id, 'prediction':pred_val_y, 'DV':val_y})
	dev_pred_df.to_csv("dev_predictions.csv", index=False)
	val_pred_df.to_csv("val_predictions.csv", index=False)

	del dev_pred_df
	del val_pred_df
	gc.collect()
	

	## Working on test data set #
	print "Working on test file.."
	test_data = pd.read_csv(test_file)
	test_X = np.array(test_data)[:,2:-1]
	test_y = np.array(test_data['DV'])
	test_device_id = np.array(test_data['device_id'])
	test_cookie_id = np.array(test_data['cookie_id'])
	del test_data
	pred_test_y = clf.predict_proba(test_X)[:,1]
	del test_X
	test_pred_df = pd.DataFrame({'device_id':test_device_id, 'cookie_id':test_cookie_id, 'prediction':pred_test_y, 'DV':test_y})
	test_pred_df.to_csv("test_predictions.csv", index=False)
