
from verdict_processor import VerdictProcessor
from utils import read_data_file_text
from pprint import pprint
import pandas as pd
import os
class VerdictQueryBuilder():
    COLUMN_ID = "id"
    COLUMN_FILE_NAME = "filename"
    COLUMN_QUERY = "query"

    def __init__(self,queries:list[str],queries_dict:dict,verdict_processor:VerdictProcessor) -> None:
        self.queries = queries
        self.queries_dict = queries_dict
        self.vedict_processor = verdict_processor
        self.processed_queries_files = None
        self.df = None

    async def build_query(self,query,indexes=None,print_file=True):
        query_files = self.queries_dict[query]
        processed_query_files = []
        if print_file:
            print("num of files in query: ",len(query_files))
            print()        
        for i,query_file in enumerate(query_files):
            if indexes is not None:
                if i not in indexes:
                    continue
            file_text = await read_data_file_text(self.vedict_processor.data_dir,self.vedict_processor.query_data_dir,query,query_file)
            if not file_text:
                return
            
            if print_file:
                print(f"{i}.",query_file)
            try:
                f = await self.vedict_processor.preprocess_file(query_file,file_text,i)
                row_start ={
                    self.COLUMN_ID:i,
                    self.COLUMN_FILE_NAME:query_file,
                    self.COLUMN_QUERY:query,
                }

                if not f:
                    row_start.update({"state":"FAIL"})
                    processed_query_files.append(row_start)
                    continue
                row_start.update(f)
                processed_query_files.append(row_start)

            except Exception as e:
                print(e)
                continue
            if print_file:
                print(" --------------- \n\n")
        
        return processed_query_files

    async def build_queries(self,override=False,indexes=None , query_indexes=None,print_query:bool=True):
        processed_queries_files = {}
        for i ,query in enumerate(self.queries):
            if indexes is not None:
                if i not in indexes:
                    continue
            if print_query:
                print("query: ", query[::-1])
            if override is False:
                filename = f"{query}.csv"
                if os.path.exists(f"./data/{query}/csv/{filename}"):
                    continue
            processed_query_files = await self.build_query(query,query_indexes,print_file=print_query)
            processed_queries_files[query] = processed_query_files
        return processed_queries_files

    async def build(self,override=False,queries_indexes=None , query_files_indexes=None, print_query=True):
        processed_queries_files = await self.build_queries(override=override,indexes=queries_indexes,query_indexes=query_files_indexes,print_query=print_query)
        self.processed_queries_files = processed_queries_files
        return processed_queries_files
    
    async def print_all(self):
        pprint(self.processed_queries_files)

    async def build_dataframe(self,override=False):
        if not self.processed_queries_files:
            return
        # rows_lst = []
        for query, value in self.processed_queries_files.items():
            filename = f"{query}.csv"
            if override is False:
                if os.path.exists(f"./data/{query}/csv/{filename}"):
                    continue
            pd.DataFrame(value).to_csv(f"./data/{query}/csv/{filename}")
        #     rows_lst.extend(value)
        # df = pd.DataFrame(rows_lst)
        # if os.path.exists("./all_data/data.csv"):
        #     pass
        # df.to_csv("./all_data/data.csv")



