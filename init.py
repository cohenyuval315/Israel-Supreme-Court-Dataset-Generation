from verdict_query_handler import VerdictQueryHandler
from verdict_query_scrapper import VerdictQueryScrapper
from verdict_processor import VerdictProcessor
from verdict_query_builder import VerdictQueryBuilder
from utils import get_data_dir
from config import Config
import os
from pprint import pprint

async def scrap_download(verdict_query_handler:VerdictQueryHandler,verdict_query_scrapper:VerdictQueryScrapper,query_search_input:str,max_files:int,retry=False):
    if retry is False:
        if os.path.exists(f"./data/{query_search_input}"):
            return
    file_links = await verdict_query_scrapper.scrap_for_file_links(query_search_input)
    await verdict_query_handler.download_files(links=file_links,
                                            max_files=max_files,
                                            query_search_input=query_search_input)
    
async def queries_build(verdict_query_handler:VerdictQueryHandler,verdict_processor:VerdictProcessor,override:bool=False):
    queries_dict = await verdict_query_handler.get_queries_dict()
    queries = await verdict_query_handler.get_all_queries()
    verdict_builder = VerdictQueryBuilder(queries,queries_dict,verdict_processor=verdict_processor)
    queries_indexes=None # [0] # only on 0
    query_files_indexes=None #[0,1]
    print_query=True
    processed_files = await verdict_builder.build(override=override,print_query=print_query,queries_indexes=queries_indexes,query_files_indexes=query_files_indexes)
    try:
        await verdict_builder.build_dataframe(override)
    except Exception as e:
        print(e)
        
    




async def init(config:Config):
    try:
        await run(config)
    except Exception as e:
        print(e)


async def run(config:Config):
    queries = config.QUERIES 
    override_exisitng_csv = config.OVERRIDE_EXISTING
    download=config.DOWNLOAD
    max_files = config.MAX_FILES_TO_DOWNLOAD_FROM_QUERY
    data_dir_name = config.ALL_DATA_DIR_NAME
    query_data_dir = config.EACH_QUERY_FILES_DIR_NAME
    query_processed_data_dir = config.EACH_QUERY_CSV_FILE_DIR_NAME
    chromedriver_path = config.CHROMEDRIVER_PATH
    query_test_input= config.QUERY_TEST_INPUT
    redownload_existing_queries = config.REDOWNLOAD_EXISITING
    data_dir = get_data_dir(data_dir_name=data_dir_name)

    # init 
    verdict_query_handler = VerdictQueryHandler(data_dir=data_dir,query_data_dir=query_data_dir,query_processed_data_dir=query_processed_data_dir,query_test_input=query_test_input)
    verdict_query_scrapper =  VerdictQueryScrapper(chromedriver_path=chromedriver_path)
    verdict_processor = VerdictProcessor(data_dir=data_dir,query_data_dir=query_data_dir,query_processed_data_dir=query_processed_data_dir)
    

    if len(queries) == 0:
        query = await verdict_query_handler.get_input_query(test=config.TEST)
        queries = []
        queries.append(query)
    

    if download:
        for query_search_input in queries:
            try:
                await scrap_download(verdict_query_handler,verdict_query_scrapper,query_search_input,max_files,retry=redownload_existing_queries)
            except Exception as e:
                print(e)
                
    
    
    await queries_build(verdict_query_handler,verdict_processor,override=override_exisitng_csv)

    # import pandas as pd
    # p = pd.read_csv("./data/דירות/csv/דירות.csv")
    # v = p.iloc[4]
    # print(v['filename'])
    # print(v['title'])
    # pprint(v['team_one_names'])
    # pprint(v['team_one'])
    # pprint(v['team_two_names'])
    # pprint(v['team_two'])


    # pprint(v['lawyers_teams_names'])
    # pprint(v['lawyers'])
    
    
    

