Order of files to run:

0. getIDV.py - Code to create the initial set of variables.

1. getIDV_IP.py - This is to produce intermediate files to form IP related variables 

2. getIDV_IP2.py - This is to create variables realted to IP for dev, val and test

3. doSampleAndMerge.py - This is to sample the dev file and reduce its size and then merge the variable csv files.
It also merges the variable csv files of val and test sample.

4. buildModel_xgb.py

5. getMetric.py
