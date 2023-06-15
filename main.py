import asyncio
from query_files_handler import QueryFilesHandler
from query_files_scrapper import QueryFilesScrapper
from files_processor import FilesProcessor
import PyPDF2
from PyPDF2 import errors
import os

def get_data_dir(data_dir_name):
    abs_path = os.path.abspath(".")
    data_dir = os.path.join(abs_path,data_dir_name)
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.exists(data_dir):
        raise Exception()
    return data_dir
    

ALL_DATA_DIR_NAME = "data"
EACH_QUERY_FILES_DIR_NAME = "pdfs"
EACH_QUERY_CSV_FILE_DIR_NAME = "csv"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
DOWNLOAD = True
MAX_FILES_TO_DOWNLOAD_FROM_QUERY = 20



async def main(download=False,max_files = 20):
    data_dir_name = ALL_DATA_DIR_NAME
    query_data_dir = EACH_QUERY_FILES_DIR_NAME
    query_processed_data_dir = EACH_QUERY_CSV_FILE_DIR_NAME
    chromedriver_path = CHROMEDRIVER_PATH

    data_dir = get_data_dir(data_dir_name=data_dir_name)
    query_files_handler = QueryFilesHandler(data_dir=data_dir,query_data_dir=query_data_dir,query_processed_data_dir=query_processed_data_dir)
    query_files_scrapper =  QueryFilesScrapper(chromedriver_path=chromedriver_path)
    file_processor = FilesProcessor(data_dir=data_dir,query_data_dir=query_data_dir,query_processed_data_dir=query_processed_data_dir)
    query_search_input = await query_files_handler.get_input_query(test=True)
    if not isinstance(query_search_input,str):
        return
    if download:
        file_links = await query_files_scrapper.scrap_for_file_links(query_search_input)
        await query_files_handler.download_files(links=file_links,
                                                max_files=max_files,
                                                query_search_input=query_search_input)
    queries_dict = await query_files_handler.get_queries_dict()
    queries = await query_files_handler.get_all_queries()
    for query in queries:
        query_files = queries_dict[query]
        print("query: ", query[::-1])
        print("num of files in query: ",len(query_files))
        print()
        for i,query_file in enumerate(query_files):
            file_text = await file_processor.read_data_file_text(query,query_file)
            print(f"{i}.",query_file)
            try:
                await file_processor.preprocess_file(file_text)
            except errors.EmptyFileError as e:
                print(e)
                continue
            except Exception as e:
                print(e)
            print()
    

if __name__ == "__main__":
    asyncio.run(main(download=DOWNLOAD,max_files=MAX_FILES_TO_DOWNLOAD_FROM_QUERY))


