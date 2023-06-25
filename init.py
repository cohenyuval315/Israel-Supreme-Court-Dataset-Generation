from verdict_query_handler import VerdictQueryHandler
from verdict_query_scrapper import VerdictQueryScrapper
from verdict_processor import VerdictProcessor
from verdict_query_builder import VerdictQueryBuilder
from utils import get_data_dir
from config import Config
import asyncio


async def scrap_download(verdict_query_handler:VerdictQueryHandler,verdict_query_scrapper:VerdictQueryScrapper,query_search_input:str,max_files:int):
    file_links = await verdict_query_scrapper.scrap_for_file_links(query_search_input)
    await verdict_query_handler.download_files(links=file_links,
                                            max_files=max_files,
                                            query_search_input=query_search_input)
    
async def queries_build(verdict_query_handler:VerdictQueryHandler,verdict_processor:VerdictProcessor):
    queries_dict = await verdict_query_handler.get_queries_dict()
    queries = await verdict_query_handler.get_all_queries()
    verdict_builder = VerdictQueryBuilder(queries,queries_dict,verdict_processor=verdict_processor)
    await verdict_builder.build()
    await verdict_builder.print_all()


async def init(config:Config):
    try:
        await run(config)
    except Exception as e:
        print(e)


async def run(config:Config):

    download=config.DOWNLOAD
    max_files = config.MAX_FILES_TO_DOWNLOAD_FROM_QUERY
    data_dir_name = config.ALL_DATA_DIR_NAME
    query_data_dir = config.EACH_QUERY_FILES_DIR_NAME
    query_processed_data_dir = config.EACH_QUERY_CSV_FILE_DIR_NAME
    chromedriver_path = config.CHROMEDRIVER_PATH
    query_test_input= config.QUERY_TEST_INPUT
    data_dir = get_data_dir(data_dir_name=data_dir_name)


    # init 
    verdict_query_handler = VerdictQueryHandler(data_dir=data_dir,query_data_dir=query_data_dir,query_processed_data_dir=query_processed_data_dir,query_test_input=query_test_input)
    verdict_query_scrapper =  VerdictQueryScrapper(chromedriver_path=chromedriver_path)
    verdict_processor = VerdictProcessor(data_dir=data_dir,query_data_dir=query_data_dir,query_processed_data_dir=query_processed_data_dir)
    

    # query
    query_search_input = await verdict_query_handler.get_input_query(test=config.TEST)

    if not query_search_input:
        print("no query")
        return
    
    if download:
        await scrap_download(verdict_query_handler,verdict_query_scrapper,query_search_input,max_files)
    
    
    await queries_build(verdict_query_handler,verdict_processor)

    

