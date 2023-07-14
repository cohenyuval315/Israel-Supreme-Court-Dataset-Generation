# Israel-Sumpreme-Court-Dataset-Generation

Creates Hebrew Verdicts Dataset From Israel Supreme Court Search Engine  
Search Engine : https://supremedecisions.court.gov.il/  

[nlp machine learning](https://github.com/cohenyuval315/Israel-Supreme-Court-Dataset-Generation/blob/master/working/working.ipynb)
trying different method of machine learning using the data generated 

# Dataset Generation
## run
```code
python main.py
```
## config
Configuration File : [Config](https://github.com/cohenyuval315/Israel-Supreme-Court-Dataset-Generation/blob/master/config.py)

- ALL_DATA_DIR_NAME :                All data directory name for all the data generated in the script.  
- QUERIES:                           List of queries. Each query will be searched on the search engine and recieve its own directory under alldata directory.  
- EACH_QUERY_FILES_DIR_NAME :        At each indivudal query direcory , a folder name for the unprocessed data.  
- EACH_QUERY_CSV_FILE_DIR_NAME:      At each indivudal query direcory , a folder name for the processed data.  
- CHROMEDRIVER_PATH:                 Your path to chrome.  
- DOWNLOAD:bool                      Download the files from web.  
- MAX_FILES_TO_DOWNLOAD_FROM_QUERY:  Max of files to download for each query , for the same query if the files exists , it wont redownload.  
- TEST:bool                          True=Not asking for input    
- OVERRIDE_EXISTING :bool            Reprocess all data generation csv files , meaning you can change the processing and change the processed csv files.  
- REDOWNLOAD_EXISITING :bool         Redownload all the files from the web.  
- QUERY_TEST_INPUT:                  Default query to search with.  


# Dataset:
- Hebrew Dataset
- Verdicts only
- Each query is a batch data.
- each batch is one csv file
- each csv file is batch of many pdfs files from the site under the search of that query.
- still need some work
### Data Colums:
- title: Verdict's Title
- date: Verdict's Date
- procedures : Verdict's list of procedures.
- judges_first_names: Verdict's judges first names.
- judges_last_names: Verdict's judges last names.
- judges_genders: Verdict's judges genders.
- team_one_names: List of the prosecution teams one names.
- team_one: List of lists of the prosecution team memebers coresponding to team_one_names
- team_one_extra: Extra information relevent to team one.
- team_two_lawyers_teams_names: List of prosecution team lawyers teams names
- team_two_lawyers : List of lists of the prosecution team lawyers memebers coresponding to team one lawyers teams names
- team_two_names: List of the defense teams names.
- team_two: List of lists of the defense team memebers coresponding to team_two_names
- team_two_extra: Extra information relevent to team two.
- team_two_lawyers_teams_names: List of defense team lawyers teams names
- team_two_lawyers : List of lists of the defense team lawyers memebers coresponding to team two lawyers teams names
- text: Complete Verdict's Text
- all_lawyers_teams_names: List all lawyers teams names 
- all_lawyers: List of lists of all lawyers presented in the Verdict











