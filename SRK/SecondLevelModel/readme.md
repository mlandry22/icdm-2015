1. dataPrep_SecondLevel.R - to prepare new variables from the predictions

2. secondModel.py - code to build the model after joining new variables with existing variables

3. getMetric_new_m2.py - Get the F0.5 metric on the for the new val sample

Improvement in AUC from 0.9946 to 0.9952 (may be due to different val samples?)

But Val sample F0.5 score remains the same. Infact 0.74 compared to 0.75 using the original model 
