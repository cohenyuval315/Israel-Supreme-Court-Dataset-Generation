from verdict_query_handler import VerdictQueryHandler
from verdict_query_scrapper import VerdictQueryScrapper
from verdict_processor import VerdictProcessor
from verdict_query_builder import VerdictQueryBuilder
from utils import get_data_dir
from config import Config
import asyncio
from pprint import pprint
from verdict_hebrew_nlp import VerdictHebrewNLP
import json
import hebrew_tokenizer as ht

async def scrap_download(verdict_query_handler:VerdictQueryHandler,verdict_query_scrapper:VerdictQueryScrapper,query_search_input:str,max_files:int):
    file_links = await verdict_query_scrapper.scrap_for_file_links(query_search_input)
    await verdict_query_handler.download_files(links=file_links,
                                            max_files=max_files,
                                            query_search_input=query_search_input)
    
async def queries_build(verdict_query_handler:VerdictQueryHandler,verdict_processor:VerdictProcessor):
    queries_dict = await verdict_query_handler.get_queries_dict()
    queries = await verdict_query_handler.get_all_queries()
    verdict_builder = VerdictQueryBuilder(queries,queries_dict,verdict_processor=verdict_processor)
    queries_indexes=[0] # only on 0
    query_files_indexes=[0,1]
    print_query=True
    processed_files = await verdict_builder.build(print_query=print_query,queries_indexes=queries_indexes,query_files_indexes=query_files_indexes)
    # await verdict_builder.print_all()
    await nlp(verdict_builder)

async def compute_idf_verdicts(vhnlp:VerdictHebrewNLP,processed_queries_files:dict):
    for query,files in processed_queries_files.items():
         for i,item in enumerate(files):
            data = item['data']
            bag_dict = await vhnlp.get_bag_of_words(data)
            await vhnlp.process_bag(file_name=files[i],bag_dict=bag_dict)

    return vhnlp.idf_dict
        
async def compute_tf_idf_verdicts(vhnlp:VerdictHebrewNLP,processed_queries_files:dict):
    for query,files in processed_queries_files.items():
         for i,item in enumerate(files):
            data = item['data']
            bag_dict = await vhnlp.get_bag_of_words(data)
            tf_bag_dict = await vhnlp.compute_tf(bag_dict=bag_dict)
            tf_idf_dict = await vhnlp.compute_tf_idf(tf_bag_dict=tf_bag_dict)
            tags,scores = await vhnlp.get_tags(tf_idf_dict)
            print(tags[-5:])
            print(scores[-5:])
            
            processed_queries_files[query][i]["tags"] = ";".join(tags)
    return processed_queries_files
        
async def nlp(verdict_builder:VerdictQueryBuilder):
    vhnlp = VerdictHebrewNLP()
    if not verdict_builder.processed_queries_files:
        return  None
    
    await compute_idf_verdicts(vhnlp=vhnlp,processed_queries_files=verdict_builder.processed_queries_files)
    taged_processed_queries_files = await compute_tf_idf_verdicts(vhnlp=vhnlp,processed_queries_files=verdict_builder.processed_queries_files)

        
    with open('processed_queries_files_example.json', 'w', encoding='utf-8') as f: 
        json.dump(taged_processed_queries_files, f, ensure_ascii=False, indent=4) 

    with open('idf_example.json', 'w', encoding='utf-8') as f: 
        json.dump(vhnlp.idf_dict, f, ensure_ascii=False, indent=4) 
        

    



    









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

    

