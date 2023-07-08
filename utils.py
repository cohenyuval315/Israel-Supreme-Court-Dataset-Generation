import regex as re
import PyPDF2
import os
import pandas as pd

def remove_extra_spaces(string):
    modified_string = re.sub(r'\s+', ' ', string)
    return modified_string

def remove_digits_and_periods(text):
    pattern = r"[0-9.]"
    cleaned_text = re.sub(pattern, "", text)
    return cleaned_text.strip()


def remove_empty_strings(lst:list):
    return [i.strip() for i in lst if len(i) > 0]

async def find_text_first_index_in_list(lst,text,reverse=False):
    index = -1
    divider = text
    if reverse:
        divider = text[::-1]
    for i, line in enumerate(lst):
        if divider in line:
            index = i
            break
    if index == -1:
        return None
    return index


def get_data_dir(data_dir_name):
    abs_path = os.path.abspath(".")
    data_dir = os.path.join(abs_path,data_dir_name)
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.exists(data_dir):
        raise Exception()
    return data_dir

async def create_processed_file(data_dir,query_processed_data_dir,dataframe:pd.DataFrame,query,file_type="csv"):
    path = os.path.join(data_dir,query,query_processed_data_dir, query + "." + file_type)
    if os.path.exists(path):
        old_pd = pd.read_csv(path)
        new_pd = pd.concat([old_pd,dataframe])
        new_pd.drop_duplicates(inplace=True)
        new_pd.reset_index(drop=True,inplace=True)
        new_pd.to_csv(path,index=False)
    else: 
        dataframe.to_csv(path,index=False)

async def make_path(data_dir,query_data_dir,query):
    return os.path.join(data_dir,query,query_data_dir)

async def read_data_file_text(data_dir,query_data_dir,query:str,filename:str):
    file_path = os.path.join(data_dir,query,query_data_dir,filename) 
    try: 
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(e)
        return None
    return text

async def extract_name(content, label):
    pattern = f'{label}: (.+)'  # assuming the name follows the label
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    else:
        return None