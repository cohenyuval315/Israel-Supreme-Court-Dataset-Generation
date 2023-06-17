import asyncio
from query_files_handler import QueryFilesHandler
from query_files_scrapper import QueryFilesScrapper
from files_processor import FilesProcessor
from PyPDF2 import errors
import os

    

ALL_DATA_DIR_NAME = "data" # the data directory in this current path , it will be created if u dont have
EACH_QUERY_FILES_DIR_NAME = "pdfs" # for each query it will create a folder and put its downloaded files into this folder name
EACH_QUERY_CSV_FILE_DIR_NAME = "csv" # for each query it will create a folder and in this folder we will keep the proccessed dataframe csv of this query
CHROMEDRIVER_PATH = "/usr/bin/chromedriver" # your path to chrome
DOWNLOAD = False # can keep at true its doesnt redownload , but it still open sellinum
MAX_FILES_TO_DOWNLOAD_FROM_QUERY = 20 # max of files to download for the chosen query , its doesnt iterate , for the same query if the files already downloaded , it wont redownload, if u put bigger number it just add the files you didnt have
TEST = True # not asking for input


async def build_csv_rows(queries,queries_dict,file_processor):

    COLUMN_ID = "id"
    COLUMN_FILE_NAME = "filename"
    COLUMN_QUERY = "query"

    processed_queries_files = {}

    for query in queries:
        query_files = queries_dict[query]
        processed_queries_files[query] = []
        print("query: ", query[::-1])
        print("num of files in query: ",len(query_files))
        print()
        processed_query_files = []
        for i,query_file in enumerate(query_files):
            file_text = await file_processor.read_data_file_text(query,query_file)
            print(f"{i}.",query_file)
            try:
                f = await file_processor.preprocess_file(file_text)
                row_start ={
                    COLUMN_ID:i,
                    COLUMN_FILE_NAME:query_file,
                    COLUMN_QUERY:query,
                }

                if not f:
                    row_start.update({"state":"FAIL"})
                    processed_query_files.append(row_start)
                    continue
                row_start.update(f)
                processed_query_files.append(row_start)
            except errors.EmptyFileError as e:
                print(e)
                continue
            except Exception as e:
                print(e)
            print()

            break
        processed_queries_files[query] = processed_query_files
        break
    return processed_queries_files


async def main(download=False,max_files = 20):
    data_dir_name = ALL_DATA_DIR_NAME
    query_data_dir = EACH_QUERY_FILES_DIR_NAME
    query_processed_data_dir = EACH_QUERY_CSV_FILE_DIR_NAME
    chromedriver_path = CHROMEDRIVER_PATH


    data_dir = get_data_dir(data_dir_name=data_dir_name)
    query_files_handler = QueryFilesHandler(data_dir=data_dir,query_data_dir=query_data_dir,query_processed_data_dir=query_processed_data_dir)
    query_files_scrapper =  QueryFilesScrapper(chromedriver_path=chromedriver_path)
    file_processor = FilesProcessor(data_dir=data_dir,query_data_dir=query_data_dir,query_processed_data_dir=query_processed_data_dir)
    query_search_input = await query_files_handler.get_input_query(test=TEST)
    if not isinstance(query_search_input,str):
        return
    if download:
        file_links = await query_files_scrapper.scrap_for_file_links(query_search_input)
        await query_files_handler.download_files(links=file_links,
                                                max_files=max_files,
                                                query_search_input=query_search_input)
    queries_dict = await query_files_handler.get_queries_dict()
    queries = await query_files_handler.get_all_queries()

    processed_queries_files = await build_csv_rows(queries,queries_dict,file_processor)
    print(processed_queries_files)
    


def get_data_dir(data_dir_name):
    abs_path = os.path.abspath(".")
    data_dir = os.path.join(abs_path,data_dir_name)
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.exists(data_dir):
        raise Exception()
    return data_dir


if __name__ == "__main__":
    asyncio.run(main(download=DOWNLOAD,max_files=MAX_FILES_TO_DOWNLOAD_FROM_QUERY))


