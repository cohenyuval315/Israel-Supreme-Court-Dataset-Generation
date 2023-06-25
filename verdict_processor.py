
import os
import pandas as pd
import PyPDF2
import regex as re
import json
from pprint import pprint
import enum
from collections import Counter
import nltk
from utils import remove_extra_spaces,find_text_first_index_in_list




class VerdictProcessor:
    COLUMN_FAIL = "None"
    COLUMN_TITLE = "title"
    COLUMS_ALEFS = "alefs"
    COLUMNS_JUDGES_FIRST_NAMES = "judge_first_names"
    COLUMNS_JUDGES_LAST_NAMES = "judge_last_names"
    COLUMNS_JUDGES_GENDERS = "judges_genders"
    COLUMN_TEAM_ONE = "team_one"
    COLUMN_TEAM_TWO = "team_two"
    COLUMN_DATE = "date"
    COLUMNS_LAWYERS = "lawyers"
    COLUMNS_TEXT = "text"
    COLUMNS_END = "end"
    COLUMN_DECISION = "decision"
    COLUMN_DATA = "data"
    

    csv_columns = []
    def __init__(self,data_dir="/home/yuval/Desktop/nlp/data2",query_data_dir = "pdfs",query_processed_data_dir = "csv") -> None:
        self.data_dir = data_dir
        self.query_data_dir = query_data_dir
        self.query_processed_data_dir = query_processed_data_dir



        


    async def area_spliting(self, text:str,id:int):
        verdict_data_divider = "דין-פסק"
        team_versus_divider =  "ד  ג  נ"
        date_verdict_sitting = "הישיבה תאריך"
        end_spliter  = "_________________________"
        before_judges_divider = "לפני"
        lawyers_prefix = "בשם"

        verdict_data_divider_index = await find_text_first_index_in_list(text.split("\n"),verdict_data_divider)
        if not verdict_data_divider_index:
            return False
        
        verdict_data = "\n".join(text.split("\n")[:verdict_data_divider_index])
        verdict_data_area = verdict_data
        verdict_text_data = "\n".join(text.split("\n")[verdict_data_divider_index:])
        
        verdict_data_split = verdict_text_data.split(end_spliter)

        verdict_text_area =  verdict_data_split[0]
        verdict_end_area = verdict_data_split[1]
        date_splitter = verdict_data.split(date_verdict_sitting)
        if len(date_splitter) == 1:
            lawyers_start_index = await find_text_first_index_in_list(date_splitter[0].split("\n"),lawyers_prefix)
            verdict_lawyer_area = "\n".join(date_splitter[0].split("\n")[lawyers_start_index:])
            verdict_teams_data = "\n".join(date_splitter[0].split("\n")[:lawyers_start_index])   
            verdict_date_area = "None"         
        else:
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

        before_judges_divider = await find_text_first_index_in_list(verdict_data_with_team1.split("\n"),before_judges_divider)
        if not before_judges_divider:
            return False
        judges_and_team1 = "\n".join(verdict_data_with_team1.split("\n")[before_judges_divider:])
        verdict_alefs_area = "\n".join(verdict_data_with_team1.split("\n")[:before_judges_divider])

        judges_and_team1_splitter = judges_and_team1.split("\n")
        judges_and_team1_splitter[0] = judges_and_team1_splitter[0].split(":")[:len(judges_and_team1_splitter[0].split(":"))-1][0]

        judges_and_team1s = "\n".join(judges_and_team1_splitter)

        teams_index = await find_text_first_index_in_list(judges_and_team1s.split("\n"),":")
        verdict_judges_area = "\n".join(judges_and_team1s.split("\n")[:teams_index])

        verdict_team_1_area = "\n".join(judges_and_team1s.split("\n")[teams_index:])


        verdict_areas = (verdict_title_area, 
                         verdict_alefs_area,
                         verdict_judges_area,
                         verdict_team_1_area,
                         verdict_team_2_area,
                         verdict_date_area,
                         verdict_lawyer_area,
                         verdict_text_area,
                         verdict_end_area,
                         verdict_data_area,
                         )
        for i in range(len(verdict_areas)):
            if len(verdict_areas[i]) == 0:
                return False
            
        return verdict_areas
    

    async def process_verdict_title(self,title:str): # done
        verdict_title = title.strip() 
        # print(verdict_title)
        return verdict_title

    async def process_verdict_alefs(self,alefs:str): # done
        lst_alefs = []
        for alef in alefs.split("\n"):
            lst_alefs.append(alef.strip())
        # print(lst_alefs)
        return lst_alefs

    async def process_verdict_judges(self,judges:str): # done
        #print("judges",judges)
        judges_first_names = []
        judges_last_names = []
        judges_genders = []
        # honor_prefix =  "כבוד"
        female_judge_prefix = "השופטת"
        female_high_judge_prefix = "הנשיאה"
        male_judge_prefix = "השופט"
        male_high_judge_prefix = "הנשיא"
        male = "male"
        female = "female"
        for judge in judges.split("\n"):
            normal_judge= await remove_extra_spaces(judge)
            judge_row = normal_judge.split(" ")
            last_name = judge_row[0]
            first_name = judge_row[1]
            gender = self.COLUMN_FAIL
            exists = False
            if judge_row[2] == male_judge_prefix or judge_row[2] == male_high_judge_prefix:
                gender = male
                exists = True
            if judge_row[2] == female_judge_prefix or judge_row[2] == female_high_judge_prefix:
                gender = female
                exists=True
            if exists:
                last_name = last_name[:len(last_name)-1] # remove the '
                judges_first_names.append(first_name)
                judges_last_names.append(last_name)
                judges_genders.append(gender)
        data = judges_first_names,judges_last_names,judges_genders
        # print(data)
        return data


    async def teams_area_spliting(self,teams_lines:list,numbers=True):
        
        team_start_signal = ":"
        if numbers:
            list_pattern = r"\.\s*\d+"
        else:
            list_pattern = r""

        i = 0
        current_team = "None" 
        teams = {
            current_team:[]
        }
        teams_extra = {
            current_team:[]
        }        
        
        while True:
            if not teams_lines[i]:
                break
            if team_start_signal in teams_lines[i]:
                team_name = teams_lines[i].split(":")[1].strip()
                rest = teams_lines[i].split(":")[0].strip()
                teams[team_name] = []
                teams_extra[team_name] = []
                if len(rest) > 0:
                    teams[team_name].append(rest)
                current_team = team_name
            else:
                current = teams_lines[i].strip()
                if len(current) > 0:
                    teams[current_team].append(current)
            if len(teams_lines) == i + 1:
                break
            i+=1
        
        del_indexes = []
        for team in teams.keys():
            for i,player in enumerate(teams[team]):
                if not re.search(list_pattern,player):
                    extra_data = player
                    teams_extra[team].append(extra_data)
                    # if i - 1 < 0:
                    #     continue
                    # teams[team][i - 1] = f"{player} " + teams[team][i - 1]
                    del_indexes.append((team,i))
        # print("hey2")
        # for del_ind in del_indexes:
        #     team_name = del_ind[0]
        #     team_del_index = del_ind[1]
        #     del teams[team_name][team_del_index]
        # print("hey1")
        
        # for team in teams.keys():
        #     for i,player in enumerate(teams[team]):
        #         new_text = re.sub(list_pattern, "", player).strip()
        #         teams[team][i] = new_text

        if len(teams['None']) == 0:
            del teams['None']
        if len(teams_extra['None']) == 0:
            del teams_extra['None']
        
        return teams,teams_extra



    async def process_verdict_team_one(self,team_one:str):
        team_lines = await self.remove_empty_strings(team_one.split("\n"))
        team_dict,team_extra = await self.teams_area_spliting(team_lines)
        return team_dict,team_extra

    async def process_verdict_team_two(self,team_two:str):
        team_lines = await self.remove_empty_strings(team_two.split("\n"))
        team_dict,team_extra = await self.teams_area_spliting(team_lines)
        return team_dict,team_extra

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

    async def remove_empty_strings(self,lst:list):
        return [i for i in lst if len(i) > 0]
            

    async def lawyers_spliting(self,teams_lines:list):
        teams_lines = await self.remove_empty_strings(teams_lines)
        team_dict,team_extra = await self.teams_area_spliting(teams_lines,False)
        for key in team_dict.keys():
            for idx, lawyer in enumerate(team_dict[key]):
                lawyers = lawyer.split(",")
                for i,item in enumerate(lawyers):
                    lawyers[i] = item.strip()
                team_dict[key] = lawyers
        return team_dict,team_extra



    async def process_verdict_lawyers(self,lawyers:str):#done
        team_dict,team_extra = await self.lawyers_spliting(lawyers.split("\n"))
        # pprint(team_dict)
        return team_dict

    async def process_verdict_text(self,text:str,alefs): # done
        text_lines = await remove_extra_spaces(text)
        text_lines = text_lines.split("\n")
        text_lines = await self.remove_empty_strings(text_lines)
        # list_pattern = r"\.\s*\d+^"
        # data =  re.split(list_pattern,text)

        verdict_accept_decisions_words = [           
            "לקבל",
            "מקבלים",
            "להסכים",
            "מסכימים",
            "מקבל",
            "מקבלת",
            "מאשרת",
            "מסכימה",
            "מסכים",
            "לאשר",
            "מאשר",
            "מאשרים",
        ]

        verdict_deny_decisions_words = [
            "לדחות",
            "נדחה",
            "נדחת",
            "לסרב" ,    
            "דוחה",
            "מסרבים",
            "מסרבת",
            "מסרב" ,     
        ]
        verdict_decision_suffix = [
            "טענה",
            "טענת",
            "טענתו",
            "טענת",
            "טענתם",
            "טענות",
            "בקשת",
            "בקשות",
            "בקשה",
            "עורעור",
            "ערעורו",
            "ערעורה",
            "בקשתו",
            "בקשת",
        ]
        verdict_finishers = [
            "סוף דבר",
        ]

        length = len(text_lines)
        l = length / 4
        max_index = -l
        index = -1
        

        indexes = []
        while index > max_index:
            l = text_lines[index]
            for item in verdict_accept_decisions_words:
                if item in l:
                    indexes.append(index)

            for item in verdict_deny_decisions_words:
                if item in l:
                    indexes.append(index)

            for item in verdict_decision_suffix:
                if item in l:
                    indexes.append(index)             

            for item in verdict_finishers:
                if item in l:
                    indexes.append(index)                                 
            
            index -= 1

        if len(indexes) != 0:
            min_index = min(indexes)
            min_index -= 10
            decision_area = "\n".join(text_lines[:min_index])
            text_area = "\n".join(text_lines[:min_index * - 1])
            return text_area,decision_area
        else:
            decision_area = ""
            text_area = "\n".join(text_lines)
            return text_area,decision_area
        

    async def process_verdict_end(self,end:str): # None
        # print("end=",end)
        return end

    async def process_verdict_decision(self,decision:str):

        verdict_deny_decisions_words = [
            "לדחות",
            "נדחה",
            "נדחת",
            "לסרב" ,    
            "דוחה",
            "מסרבים",
            "מסרבת",
            "מסרב" ,     
        ]
        verdict_decision_suffix = [
            "טענה",
            "טענת",
            "טענתו",
            "טענת",
            "טענתם",
            "טענות",
            "בקשת",
            "בקשות",
            "בקשה",
            "עורעור",
            "ערעורו",
            "ערעורה",
            "בקשתו",
            "בקשת",
        ]
        verdict_finishers = [
            "סוף דבר",
        ]


        return decision
    
    async def process_list_to_str(self,lst:list) -> str:
        l = "[" + ";".join(lst) + "]"
        return l

    async def process_dict_to_str(self,dict:dict) -> str:
        # print(str(dict))
        # str_dict = json.dumps(dict)
        # str_dict = str_dict.strip()
        dict_string = ""
        for key in dict.keys():
            dict[key] =  await self.process_col_item(dict[key])
        for key in dict.keys():
            dict_string += key + ":" + dict[key] +";"
        dict_string = dict_string[ :len(dict_string) - 1]
        return dict_string
        
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
        

        


    async def preprocess_file(self,file_name:str,text:str,id:int):
        verdict_areas = await self.area_spliting(text=text,id=id)
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
        verdict_end_area,
        verdict_data_area,
        ) = verdict_areas
        
        
            

        
        title = await self.process_verdict_title(verdict_title_area)
        alefs = await self.process_verdict_alefs(verdict_alefs_area)
        judges_first_names,judges_last_names,judges_genders = await self.process_verdict_judges(verdict_judges_area)
        


        team_one,team_one_extra = await self.process_verdict_team_one(verdict_team_1_area)
        team_two,team_two_extra = await self.process_verdict_team_two(verdict_team_2_area)
        
        date = await self.process_verdict_date(verdict_date_area)
        lawyers = await self.process_verdict_lawyers(verdict_lawyer_area)
        text_data,decision = await self.process_verdict_text(verdict_text_area,alefs)
        decision = await self.process_verdict_decision(decision)
        end = await self.process_verdict_end(verdict_end_area)

        
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
            self.COLUMN_DECISION:decision,
            self.COLUMN_DATA:text_data
            # self.COLUMNS_BAG_OF_WORDS:bag_of_words,
            # self.COLUMNS_TEXT_BAG_OF_WORDS:text_bag_of_words,
        }
        return columns
        
        

