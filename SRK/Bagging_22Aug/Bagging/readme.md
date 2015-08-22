Order of files to run 

 1. doSampleAndMerge_seed1234.py
 2. doSampleAndMerge_seed4567.py
 3. buildModel_seed1234_d5.py
 4. buildModel_seed1234_d8.py
 5. buildModel_seed4567_d5.py
 6. buildModel_seed4567_d8.py
 
doSampleAndMerge will create two different datasets for running models. Only the development sample varies.
 
buildModel*.py - these will run models on the created datasets
