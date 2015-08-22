First we need to run the codes present inside the bagging folder. 
But instead we could safely use the predcitions file (val_predictions.7z and test_predictions.7z) shared in the google drive.

Using the above prediction files in shared folder, we can run the following codes
 1. dataPrep_secondModel.py - added few extra vars from our previous version
 2. secondModel.py - differs in xgboost params -will output csv files which are also present in google drive (dev_predictions_m2.7z, val_predictions_m2.7z, test_predictions_m2.7z)
 3. getMetric_secondModel.py - differs slightly than last one
 
Alternatively, we could also just run the 3rd code (getMetric_secondModel.py) after taking the output files of second code from google drive.
This can save us some more time.
