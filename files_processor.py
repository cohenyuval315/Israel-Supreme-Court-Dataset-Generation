
import os
import pandas as pd
import PyPDF2
import regex as re

judgement_id_col = "id"
verdict_id_col = "verdict_id"
judges_col = "judges"
judges_genders_col = "genders"
judgement_name_col = "name"
prosecutor_col = "prosecutors"
defendant_col = "defendants"
judgement_subjects_tags_col = "tags" # 2-5 for each , string,string,string,
sentiment_analysis_col = "sentiment" # negative neutural positive  , -1 0 , 1


class FilesProcessor:
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

    async def preprocess_file(self,text:str):
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

        
        before_judges_start_index =  await self.find_text_first_index_in_list(lines,before_judges_divider1)
        if before_judges_start_index is None:
            print("no index for before")
            return        
        
        i = 0
        while True:
            if before_judges_divider1 not in lines[i]:
                i +=1
                alefs.append(lines[i - 1])
            else:
                break
        lines = lines[i:]
        lines[0] = lines[0].split(before_judges_divider1)[1:][0]
        judges = []
        genders = []
        male = 0
        female = 1
        i = 0
        while True:
            if honor_prefix[::-1] in lines[i]:
                line = lines[i].split(honor_prefix[::-1])
                if female_judge_prefix[::-1] in line[1]:
                    judge = line[1].split(female_judge_prefix[::-1])[1]
                    judges.append(judge.strip() )
                    genders.append(female)

                else:
                    if male_judge_prefix[::-1] in line[1]:
                        judge = line[1].split(male_judge_prefix[::-1])[1]
                        judges.append(judge.strip() )
                        genders.append(male)                        
            else:
                break
            i+=1
        print(alefs)
        print(judges)
        print(genders)


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
            
        

        verdict_divider = "דין-פסק"
        
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

    async def extract_name(self,content, label):
        pattern = f'{label}: (.+)'  # assuming the name follows the label
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        else:
            return None

