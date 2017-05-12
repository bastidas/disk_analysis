
An analysis of hard drive data from the Backblaze which includes 15 Gig of data going back to 2013 including 90 columns of raw and normalized SMART hard drive statistics which offer the ability to predict hard drive failure. In particular this analysis analysis:
 * Cleans the data and summarizes by year.
 * Makes naive failure rate predictions.
 * Makes a survival tables of each individual hard drive model in the data set.
 * Does survival analysis in order to predict failure rates with uncertainty estimates, robust prediction of failure rate.
 * Applys machine learning (random forest, tensorflow) to predict pending hard drive failures


[The main result of this project is this web page that presents the results](https://hard-drives.herokuapp.com)


 The steps to recreate this analysis:
 1) Get the data by running Download_Data.ipynb
 2) Make a summaries of the data by running HD_Model_Summary_Gen.ipynb
 3) Make surival tables of the data by running HD_Survival_Table_Gen
 4)
     * HD_Survival_Analysis.ipynb can now be run to do surival rates with Kaplan-Mier and hazard rates with Nelson-Aalen
 5) Generate the daily stats for a single model (by deault the most common drive in the data set) by running HD_Model_Data_Gen.ipynb
 6) Extract the relevant features and munge data further with HD_Extract_Features.ipynb
     * HD_Learned_Importance.ipynb can now be run
     * HD_Predict_Failure can now be run
     * HD_TF_Model.py can now be run. Note that this is a python program written in python 3.5 and uses the Tensorflow library. 
     
Many of the plots seen on the webpage are created in some form in the notebooks above, but many more plotting programs are contained in the web directory.
     