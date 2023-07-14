# scraping_and_processing_hebrew_court_files

Creates Dataset From Israel Supreme Court Search Engine  
Search Engine : https://supremedecisions.court.gov.il/  

[nlp machine learning](https://github.com/cohenyuval315/Israel-Supreme-Court-Dataset-Generation/blob/master/working/working.ipynb)
trying different method of machine learning using the data generated 

# Database Generation
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


