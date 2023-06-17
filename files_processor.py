
import os
import pandas as pd
import PyPDF2
import regex as re
import json
import enum

judgement_id_col = "id"
verdict_id_col = "verdict_id"
judges_col = "judges"
judges_genders_col = "genders"
judgement_name_col = "name"
prosecutor_col = "prosecutors"
defendant_col = "defendants"
judgement_subjects_tags_col = "tags" # 2-5 for each , string,string,string,
sentiment_analysis_col = "sentiment" # negative neutural positive  , -1 0 , 1


async def remove_extra_spaces(string):
    # Replace multiple consecutive spaces with a single space
    modified_string = re.sub(r'\s+', ' ', string)
    return modified_string


class Sentiment(enum.Enum):
    POSITIVE = "positive"
    NETURAL = "netural"
    NEGATIVE = "negative"

class FilesProcessor:
    COLUMN_FAIL = "None"
    COLUMN_TITLE = "title"
    COLUMS_ALEFS = "alefs"
    # COLUMNS_JUDGES = "judges"
    COLUMNS_JUDGES_FIRST_NAMES = "judge_first_names"
    COLUMNS_JUDGES_LAST_NAMES = "judge_last_names"
    COLUMNS_JUDGES_GENDERS = "judges_genders"
    COLUMN_TEAM_ONE = "team_one"
    COLUMN_TEAM_TWO = "team_two"
    COLUMN_DATE = "date"
    COLUMNS_LAWYERS = "lawyers"
    COLUMNS_TEXT = "text"
    COLUMNS_END = "end"

    COLUMNS_TAGS = "tags"
    COLUMNS_SENTIMENT = "sentiment"


    


    csv_columns = []
    def __init__(self,data_dir="/home/yuval/Desktop/nlp/data2",query_data_dir = "pdfs",query_processed_data_dir = "csv") -> None:
        self.data_dir = data_dir
        self.query_data_dir = query_data_dir
        self.query_processed_data_dir = query_processed_data_dir

    async def _make_path(self,query):
        return os.path.join(self.data_dir,query,self.query_data_dir)

    async def create_data_pd(self):
        dataframe = pd.DataFrame(columns=[])

    async def create_processed_file(self,dataframe:pd.DataFrame,query,file_type="csv"):
        path = os.path.join(self.data_dir,query,self.query_processed_data_dir, query + "." + file_type)
        if os.path.exists(path):
            old_pd = pd.read_csv(path)
            new_pd = pd.concat([old_pd,dataframe])
            new_pd.drop_duplicates(inplace=True)
            new_pd.reset_index(drop=True,inplace=True)
            new_pd.to_csv(path,index=False)
        else: 
            dataframe.to_csv(path,index=False)

    async def read_data_file_text(self,query:str,filename:str):
        file_path = os.path.join(self.data_dir,query,self.query_data_dir,filename) 
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    async def extract_name(self,content, label):
        pattern = f'{label}: (.+)'  # assuming the name follows the label
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        else:
            return None
        
    async def find_text_first_index_in_list(self,lst,text,reverse=False):
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

    async def area_spliting(self, text:str):
        verdict_data_divider = "דין-פסק"
        team_versus_divider =  "ד  ג  נ"
        date_verdict_sitting = "הישיבה תאריך"
        end_spliter  = "_________________________"
        before_judges_divider = "לפני"

        verdict_data_divider_index = await self.find_text_first_index_in_list(text.split("\n"),verdict_data_divider)
        if not verdict_data_divider_index:
            return False
        verdict_data = "\n".join(text.split("\n")[:verdict_data_divider_index])
        verdict_text_data = "\n".join(text.split("\n")[verdict_data_divider_index:])
        
        verdict_data_split = verdict_text_data.split(end_spliter)

        verdict_text_area =  verdict_data_split[0]
        verdict_end_area = verdict_data_split[1]
        
        date_splitter = verdict_data.split(date_verdict_sitting)
        verdict_teams_data = date_splitter[0]
        verdict_lawyer_area = date_splitter[1]


        date_index = len(verdict_teams_data.split("\n"))-1
        verdict_date_area = verdict_teams_data.split("\n")[date_index]
        verdict_teams_data = "\n".join(verdict_teams_data.split("\n")[:date_index])
        team_splitter = verdict_teams_data.split(team_versus_divider)
        verdict_data_with_team1 = team_splitter[0]
        verdict_team_2_area = team_splitter[1]
    

        title_index = 0
        verdict_title_area = verdict_data_with_team1.split("\n")[title_index]


        verdict_data_with_team1 = "\n".join(verdict_data_with_team1.split("\n")[title_index + 1:])

        before_judges_divider = await self.find_text_first_index_in_list(verdict_data_with_team1.split("\n"),before_judges_divider)
        if not before_judges_divider:
            return False
        judges_and_team1 = "\n".join(verdict_data_with_team1.split("\n")[before_judges_divider:])
        verdict_alefs_area = "\n".join(verdict_data_with_team1.split("\n")[:before_judges_divider])

        judges_and_team1_splitter = judges_and_team1.split("\n")
        judges_and_team1_splitter[0] = judges_and_team1_splitter[0].split(":")[:len(judges_and_team1_splitter[0].split(":"))-1][0]

        judges_and_team1s = "\n".join(judges_and_team1_splitter)

        teams_index = await self.find_text_first_index_in_list(judges_and_team1s.split("\n"),":")
        verdict_judges_area = "\n".join(judges_and_team1s.split("\n")[:teams_index])

        verdict_team_1_area = "\n".join(judges_and_team1s.split("\n")[teams_index:])


        verdict_areas = (verdict_title_area, verdict_alefs_area,verdict_judges_area,verdict_team_1_area,verdict_team_2_area,verdict_date_area,verdict_lawyer_area,verdict_text_area,verdict_end_area)
        for i in range(len(verdict_areas)):
            if len(verdict_areas[i]) == 0:
                return False
            
        return verdict_areas
    

    async def process_verdict_title(self,title:str): # done
        verdict_title = title.strip() 
        return verdict_title

    async def process_verdict_alefs(self,alefs:str): # done
        lst_alefs = []
        for alef in alefs.split("\n"):
            lst_alefs.append(alef.strip())
        return alefs

    async def process_verdict_judges(self,judges:str): # done
        #print("judges",judges)
        judges_first_names = []
        judges_last_names = []
        judges_genders = []
        # honor_prefix =  "כבוד"
        female_judge_prefix = "השופטת"
        male_judge_prefix = "השופט"
        male = "male"
        female = "female"
        for judge in judges.split("\n"):
            normal_judge= await remove_extra_spaces(judge)
            judge_row = normal_judge.split(" ")
            last_name = judge_row[0]
            first_name = judge_row[1]
            gender = self.COLUMN_FAIL
            if judge_row[2] == male_judge_prefix:
                gender = male
            if judge_row[2] == female_judge_prefix:
                gender = female
            last_name = last_name[:len(last_name)-1] # remove the '
            judges_first_names.append(first_name)
            judges_last_names.append(last_name)
            judges_genders.append(gender)
        data = judges_first_names,judges_last_names,judges_genders
        return data

    async def parse_string(self,string):
        pattern = r'([^:\n]+):\s*(\w+)'
        matches = re.findall(pattern, string)
        result = {}
        for content,title  in matches:
            result.setdefault(title, []).append(content.strip())
        return result
    
    
    async def process_verdict_team_one(self,team_one:str):
        indexes = await self.teams_area_spliting(team_one)
        team_one_lines = team_one.split("\n")
        index_indexes = 0
        parsed_dict = await self.parse_string(team_one)
        return parsed_dict

    async def process_verdict_team_two(self,team_two:str):
        t = await self.parse_string(team_two)
        print("t=",t)
        #print("team_two=",team_two)
        return team_two

    async def process_verdict_date(self,date:str): #done
        start_date = "("
        end_date = ")"
        start_index = -1
        end_index = -1
        for i,s in enumerate(date):
            if s is start_date:
                start_index = i           
            if s is end_date:
                end_index = i
        if start_index == -1 or end_index == -1:
            return None
        d = date[start_index+1:end_index].strip()
        return d

    async def process_verdict_lawyers(self,lawyers:str):
        # print("lawyers=",lawyers)
        lay = await self.parse_string(lawyers)
        print("lawyer",lay)
        return lawyers

    async def process_verdict_text(self,text:str): # done
        # print("text=",text)
        return "verdict text" # CHANGE TO TEXT

    async def process_verdict_end(self,end:str): # None
        # print("end=",end)
        return "Dont Care"

    
    async def teams_area_spliting(self,team_text:str):
        indexes = []
        for i,line in enumerate(team_text.split("\n")):
            if ":" in line:
                indexes.append(i)
        return indexes

    async def process_list_to_str(self,lst:list) -> str:
        l = ";".join(lst)
        return l

    async def process_dict_to_str(self,dict:dict) -> str:
        # print(str(dict))
        # str_dict = json.dumps(dict)
        # str_dict = str_dict.strip()
        return str(dict)
        
    async def process_str_to_dict(self,str_dict:str) -> dict:
        # d = json.loads(str_dict)
        return eval(str_dict)

    async def process_str_to_list(self,str_list:str) -> list:
        lst = str_list.split(";")
        return lst
    

    async def process_col_item(self,col_item):
        if isinstance(col_item,list):
            if len(col_item) == 0:
                return self.COLUMN_FAIL 
            col_item =  await self.process_list_to_str(col_item)
            return col_item
        
        if isinstance(col_item,str):
            if len(col_item) == 0:
                return self.COLUMN_FAIL
            col_item =  col_item.strip()
            return col_item

        if isinstance(col_item,dict):
            if len(col_item.keys()) == 0:
                return self.COLUMN_FAIL
            col_item = await self.process_dict_to_str(col_item)
            return col_item
        
        if col_item is None:
            return self.COLUMN_FAIL
        
        if col_item is False:
            return self.COLUMN_FAIL
        
        return self.COLUMN_FAIL
        
    async def get_sentiment(self,text):
        return Sentiment.NETURAL

    async def get_tags(self,text):
        tag1 = "tag1"
        tag2 = "tag2"
        return [tag1,tag2]

    async def preprocess_file(self,text:str):
        verdict_areas = await self.area_spliting(text=text)
        if verdict_areas is False:
            return False
        
        (verdict_title_area,
        verdict_alefs_area,
        verdict_judges_area,
        verdict_team_1_area,
        verdict_team_2_area,
        verdict_date_area,
        verdict_lawyer_area,
        verdict_text_area,
        verdict_end_area) = verdict_areas



        title = await self.process_verdict_title(verdict_title_area)
        alefs = await self.process_verdict_alefs(verdict_alefs_area)
        judges_first_names,judges_last_names,judges_genders = await self.process_verdict_judges(verdict_judges_area)
        team_one = await self.process_verdict_team_one(verdict_team_1_area)
        team_two = await self.process_verdict_team_two(verdict_team_2_area)
        date = await self.process_verdict_date(verdict_date_area)
        lawyers = await self.process_verdict_lawyers(verdict_lawyer_area)
        text_data = await self.process_verdict_text(verdict_text_area)
        end = await self.process_verdict_end(verdict_end_area)

        tags = await self.get_tags(text_data)
        sentiment = await self.get_sentiment(text_data)

        
        title = await self.process_col_item(title)
        alefs =  await self.process_col_item(alefs)
        judges_first_names =  await self.process_col_item(judges_first_names)
        judges_last_names =  await self.process_col_item(judges_last_names)
        judges_genders = await self.process_col_item(judges_genders)
        
        team_one =  await self.process_col_item(team_one)
        team_two =  await self.process_col_item(team_two)
        date =  await self.process_col_item(date)
        lawyers =  await self.process_col_item(lawyers)
        text_data =  await self.process_col_item(text_data)
        end =  await self.process_col_item(end)


        tags = await self.process_col_item(tags)
        sentiment = await self.process_col_item(sentiment)

        columns = {
            self.COLUMN_TITLE :title,
            self.COLUMS_ALEFS:alefs,
            self.COLUMNS_JUDGES_FIRST_NAMES:judges_first_names,
            self.COLUMNS_JUDGES_LAST_NAMES:judges_last_names,
            self.COLUMNS_JUDGES_GENDERS:judges_genders,
            self.COLUMN_TEAM_ONE:team_one,
            self.COLUMN_TEAM_TWO:team_two,
            self.COLUMN_DATE:date,
            self.COLUMNS_LAWYERS:lawyers,
            self.COLUMNS_TEXT:text_data,
            self.COLUMNS_END:end,
            self.COLUMNS_TAGS:tags,
            self.COLUMNS_SENTIMENT:sentiment,
        }
        return columns


        return
        lines = text.strip().split('\n')
        lines = [line[::-1] for line in lines]
        verdict_title = lines[0]
        alefs = []
        lines = lines[1:]
        honor_prefix =  "כבוד"
        before_judges_divider1 = "ינפל :"
        before_judges_divider2 = "לפני :"
        female_judge_prefix = "תטפושה"
        male_judge_prefix = "טפושה"
        female_judge_prefix = "השופטת"
        male_judge_prefix = "השופט"
        date_verdict_sitting = "הישיבה תאריך"

        verdict_divider = "דין-פסק"
        

        before_judges_start_index =  await self.find_text_first_index_in_list(lines,before_judges_divider1)
        if before_judges_start_index is None:
            print("no index for before")
            return        
        
        verdict_date = None
        print(alefs)
        print(judges)
        print(genders)
        if len(judges) == 0:
            return False
        if len(alefs) == 0:
            return False
        if len(genders) == 0:
            return False

        for line in lines:
            # print(line)
            if date_verdict_sitting[::-1] in line:
                verdict_date = line[::-1].split(" ")[0]
        if not verdict_date:
            return False
        
        print(verdict_date)


        spliter = text.split(verdict_divider)
        verdict_text = spliter[1]
        verdict_data = spliter[0]
        #print(verdict_data)
        versus_divider =  "ד  ג  נ"
        spliter_data = verdict_data.split(versus_divider)
        team1 = spliter_data[0]
        team2 = spliter_data[1]
        
        spl = verdict_text.split("_________________________")
        l_s = len(spl)
        print(l_s)
        print(spl[1])
        


        male_petitioners = "העותרים:"
        male_petitioner =  "העותר:"
        female_petitioner = "העותרת:"
        female_petitioners = "העותרות:"

        male_appealer = "המערער:"
        male_appealers = "המערערים:"
        female_appealer = "המערערת:"
        female_appealers = "המערערות:"
        
        male_requester = "המבקש:"
        female_requester = "המבקשת:"
        male_requesters = "המבקשים:"
        female_requesters = "המבקשות:"
        

        
        if len(alefs) > 1:
            pass

        "versus"

        appealr_and = "והמשיבים"
        versus_small = "כשנגד:"

            

        'המערער בע"א'
        'המערערת בע"א'
        'המערערים בע"א'
        'המערערות בע"א'

        'העותרים בבג"ץ'
        'העותרות בבג"ץ'
        'העותר בבג"ץ'
        'העותרת בבג"ץ'

        return





        # if len(lines[0].split(before_judges_divider)) > 1:
        #     pass
        # return

        

        # print(before_judges_start_index)
        # l = lines[before_judges_start_index]

        # print(l)

        # print(lines[before_judges_start_index].split(before_judges_divider))[1:]

        # appealers_divider_multiple = "תורערעמה:"
        # appealers_divider_multiple = "םירערעמה:"
        # appealers_divider_single_male = "רערעמה :"
        # appealers_divider_single_female = "תרערעמה :"


        "בשם העותר:"
        "בשם העותרת:"
        "בשם העותרים:"
        "בשם העותרות:"

 
        "בשם המבקשת:"
        "בשם המבקש:"
        "בשם המבקשים:"
        "בשם המבקשות:"

        "בשם המשיב:"
        "בשם המשיבה:"
        "בשם המשיבות:"
        "בשם המשיבים:"
        "המשיב:"
        "המשיבה:"
        "המשיבים:"
        "המשיבות:"


        



        'המשיבים בע"א'
        'המשיבות בע"א'
        'המשיב בע"א'
        'המשיבה בע"א'

        "בשם המערערות:"

        # before_judges_end_index_appealer_start_index = await self.find_text_first_index_in_list(lines,appealers_divider_single) or  await self.find_text_first_index_in_list(lines,appealers_divider_multiple)



        appealer_end_index = -1


        # for l in lines:
        #     print(l)
            
        


        lawyer_prefix = 'וע"ד'

        
        
        
        
        index = -1
        for i,line in enumerate(lines):
            if verdict_divider[::-1] in line:
                index = i
                break
        if index == -1:
            print("fail")
            return

        verdit_data = lines[:index]
        verdit_text = lines[index:]

        
        



        versus_divider = "נ  ג  ד"

        replyer_divider1 = "םיבישמה:"
        replyer_divider2 = "בישמה:"
        replyer_divider3 = "הבישמה:"

        date_of_sitting = "ךיראת הבישיה :"

        in_appealers = "םשב רערעמה :"

        in_replyers_divider1 = "םשב םיבישמה"
        in_replyers_divider2 = "םשב םיבישמה"
        in_replyers_divider3 = "םשב בישמה"
        in_replyers_divider4 = "םשב הבישמה"
        in_replyers_divider_end = ":"
        in_replyers_divider_end_multiple = "-"
        
        

        index = -1
        for i, line in enumerate(verdit_data):
            if versus_divider in line:
                index = i
                break
        if index == -1:
            print("fail")
        verdit_title = verdit_data[0]
        verdit_ayin_alef = verdit_data[1]
        verdit_data = verdit_data[2:]
        
        # print(verdit_data)



        lines = [line for line in lines if re.match(judge_prefix[::-1],line) is not None]
        
        # for line in lines:
        #     print(line.split(" "))
        # print(lines)
        # 
        # print( == "דובכ")
        # match = re.match("דובכ",lines[4])
        # print(match)
        # print(lines[4])
        

