import os
import urllib.request



class QueryFilesHandler():
    TEST_QUERY_INPUT = "דירות"
    QUERY_PROMPT = "write 'exit' to leave else: \n please enter query: \n\n"
    def __init__(self,data_dir,query_data_dir,query_processed_data_dir) -> None:
        self.data_dir = data_dir
        self.query_data_dir = query_data_dir
        self.query_processed_data_dir = query_processed_data_dir
        self.queries_dict = self.build_queries_dict()

    def build_queries_dict(self,file_type="pdf"):
        result_dict = {}
        for root, dirs, files in os.walk(self.data_dir):
            if root == self.data_dir:
                continue
            dir_name = os.path.basename(root)
            pdfs_dir = os.path.join(root,self.query_data_dir)
            if not os.path.isdir(pdfs_dir):
                continue
            pdf_list = []
            for file in os.listdir(pdfs_dir):
                if file.endswith("." + file_type):
                    pdf_list.append(file)
            result_dict[dir_name] = pdf_list
        self.queries_dict = result_dict
        return result_dict
    
    async def get_queries_dict(self):
        return self.queries_dict
        
    async def get_input_query(self,test=False):
        if test is True:
            return self.TEST_QUERY_INPUT
        search_input = input(self.QUERY_PROMPT)
        if search_input == "exit":
            return None
        return search_input
    
    async def get_all_queries(self):
        queries = [query for query in self.queries_dict.keys()]
        return queries
    
    async def get_filename(self,link:str, file_type="pdf"):
        filename = link.split("fileName")[1].split(".")[0][1:]
        return filename + "." + file_type

    async def download_files(self,links:list[str],max_files:int,query_search_input:str,file_type:str="pdf"):
        query_file_names = []
        for i,link in enumerate(links):
            if i == max_files:
                break
            file_name = await self.get_filename(link,file_type)
            query_file_names.append(file_name)
            await self.download_file(file_name,link,query_search_input)    

    async def download_file(self,filename:str,link:str,query:str):
        if not os.path.exists(os.path.join(self.data_dir,query,self.query_data_dir)):
            os.makedirs(os.path.join(self.data_dir,query,self.query_data_dir))
        if not os.path.exists(os.path.join(self.data_dir,query,self.query_processed_data_dir)):
            os.makedirs(os.path.join(self.data_dir,query,self.query_processed_data_dir))    
        save_path = os.path.join(self.data_dir,query,self.query_data_dir,filename)
        if os.path.exists(save_path):
            pass
        else:
            urllib.request.urlretrieve(link, save_path)

