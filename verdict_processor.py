
import os
import pandas as pd
import PyPDF2
import regex as re
import json
from pprint import pprint
import enum
from collections import Counter
import nltk
from utils import remove_extra_spaces,find_text_first_index_in_list,remove_digits_and_periods,remove_empty_strings


class VerdictProcessor:
    COLUMN_FAIL = "None"
    COLUMN_TITLE = "title"
    COLUMS_ALEFS = "alefs"
    COLUMN_TEAM_ONE_NAMES = "team_one_names"
    COLUMN_TEAM_TWO_NAMES = "team_two_names"
    COLUMNS_JUDGES_FIRST_NAMES = "judge_first_names"
    COLUMNS_JUDGES_LAST_NAMES = "judge_last_names"
    COLUMNS_JUDGES_GENDERS = "judges_genders"
    COLUMN_TEAM_ONE = "team_one"
    COLUMN_TEAM_TWO = "team_two"
    COLUMN_DATE = "date"
    COLUMNS_LAWYERS_TEAMS = "lawyers_teams_names"
    COLUMNS_LAWYERS = "lawyers"
    COLUMNS_TEXT = "text"
    COLUMNS_END = "end"
    COLUMN_DECISION = "decision"
    COLUMN_DATA = "data"
    
    COLUMN_TEAM_ONE_EXTRA_NAMES = "team_one_extra_names"
    COLUMN_TEAM_ONE_EXTRA = "team_one_extra"
    COLUMN_TEAM_TWO_EXTRA_NAMES = "team_two_extra_names"
    COLUMN_TEAM_TWO_EXTRA = "team_two_extra"


    csv_columns = []
    def __init__(self,data_dir,query_data_dir,query_processed_data_dir) -> None:
        self.data_dir = data_dir
        self.query_data_dir = query_data_dir
        self.query_processed_data_dir = query_processed_data_dir


    async def area_spliting(self, text:str,id:int):
        verdict_data_divider = "דין-פסק"
        team_versus_divider =  "ד  ג  נ"
        date_verdict_sitting = "הישיבה תאריך"
        before_judges_divider = "לפני"
        lawyers_prefix = "בשם"

        verdict_data_divider_index = await find_text_first_index_in_list(text.split("\n"),verdict_data_divider)
        if not verdict_data_divider_index:
            return False
        
        verdict_data = "\n".join(text.split("\n")[:verdict_data_divider_index])
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
                         text
                         )
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
        return lst_alefs

    async def process_verdict_judges(self,judges:str): # done
        judges_first_names = []
        judges_last_names = []
        judges_genders = []
        female_judge_prefix = "השופטת"
        female_high_judge_prefix = "הנשיאה"
        male_judge_prefix = "השופט"
        male_high_judge_prefix = "הנשיא"
        male = "male"
        female = "female"
        for judge in judges.split("\n"):
            normal_judge= remove_extra_spaces(judge)
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
                last_name = last_name[:len(last_name)-1]
                judges_first_names.append(first_name)
                judges_last_names.append(last_name)
                judges_genders.append(gender)
        data = judges_first_names,judges_last_names,judges_genders
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
                    del_indexes.append((team,i))

        if len(teams['None']) == 0:
            del teams['None']
        if len(teams_extra['None']) == 0:
            del teams_extra['None']
        
        return teams,teams_extra



    async def process_verdict_team(self,team:str):
        team_lines = remove_empty_strings(team.split("\n"))
        team_dict,team_extra = await self.teams_area_spliting(team_lines)
        values = []
        extra = []

        for key in team_dict.keys():
            values.append(team_dict[key])

        for key in team_extra.keys():
            extra.append(team_extra[key])

        keys = list(team_dict.keys())
        extra_keys = list(team_extra.keys())
        return keys,values,extra_keys,extra

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


    async def lawyers_spliting(self,teams_lines:list):
        teams_lines = remove_empty_strings(teams_lines)
        team_dict,team_extra = await self.teams_area_spliting(teams_lines,False)
        for key in team_dict.keys():
            for idx, lawyer in enumerate(team_dict[key]):
                lawyers = lawyer.split(",")
                for i,item in enumerate(lawyers):
                    lawyers[i] = item.strip()
                team_dict[key] = lawyers
        return team_dict,team_extra



    async def process_verdict_lawyers(self,lawyers:str): # done
        team_dict,team_extra = await self.lawyers_spliting(lawyers.split("\n"))
        values = []
        extra = []

        for key in team_dict.keys():
            lst = team_dict[key]
            # lst = [l for l in lst if len(l.split(" ")) < 4]
            values.append(lst)

        for key in team_extra.keys():
            extra.append(team_extra[key])     
        
        keys = list(team_dict.keys())
        extra_keys = list(team_extra.keys())

    

        return keys,values,extra_keys,extra

    async def process_verdict_text(self,text:str): # done
        return text

        

    async def process_verdict_end(self,end:str): # None
        # print("end=",end)
        return end

    async def process_verdict_decision(self,decision:str):
        return decision
    
    async def process_list_to_str(self,lst:list) -> str:
        l = "[" + ",".join(lst) + "]"
        return l

    async def process_dict_to_str(self,dict:dict) -> str:
        dict_string = ""
        for key in dict.keys():
            dict[key] =  await self.process_col_item(dict[key])
        for key in dict.keys():
            dict_string += key + ":" + dict[key]
        dict_string = dict_string[ :len(dict_string) - 1]
        return dict_string
        
    async def process_str_to_dict(self,str_dict:str) -> dict:
        # d = json.loads(str_dict)
        return eval(str_dict)

    async def process_str_to_list(self,str_list:str) -> list:
        lst = str_list.split(",")
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
        text) = verdict_areas
        
        
        title = await self.process_verdict_title(verdict_title_area)
        alefs = await self.process_verdict_alefs(verdict_alefs_area)
        judges_first_names,judges_last_names,judges_genders = await self.process_verdict_judges(verdict_judges_area)
        
        team_one_names, team_one,team_one_extra_names,team_one_extra = await self.process_verdict_team(verdict_team_1_area)
        team_two_names,team_two,team_two_extra_names,team_two_extra = await self.process_verdict_team(verdict_team_2_area)
        
        date = await self.process_verdict_date(verdict_date_area)
        lawyers_teams,lawyers,lawyers_extra_teams,lawyers_extra = await self.process_verdict_lawyers(verdict_lawyer_area)
        
        for i,lst in enumerate(team_one):
            for j,item in enumerate(lst):
                team_one[i][j] =  remove_extra_spaces(remove_digits_and_periods(item))

        for i,lst in enumerate(team_two):
            for j,item in enumerate(lst):
                team_two[i][j] =  remove_extra_spaces(remove_digits_and_periods(item))

        for i,lst in enumerate(lawyers):
            for j,item in enumerate(lst):
                l = lawyers[i][j].split(";")
                l = remove_empty_strings(l)
                if len(l) > 1:
                    lawyers[i] = l
        
        columns = {
            self.COLUMN_TITLE :title,
            self.COLUMS_ALEFS:alefs,
            self.COLUMNS_JUDGES_FIRST_NAMES:judges_first_names,
            self.COLUMNS_JUDGES_LAST_NAMES:judges_last_names,
            self.COLUMNS_JUDGES_GENDERS:judges_genders,
            self.COLUMN_TEAM_ONE_NAMES:team_one_names,
            self.COLUMN_TEAM_ONE:team_one,
            self.COLUMN_TEAM_ONE_EXTRA_NAMES:team_one_extra_names,
            self.COLUMN_TEAM_ONE_EXTRA:team_one_extra,
            
            self.COLUMN_TEAM_TWO_NAMES:team_two_names,
            self.COLUMN_TEAM_TWO:team_two,
            self.COLUMN_TEAM_ONE_EXTRA_NAMES:team_two_extra_names,
            self.COLUMN_TEAM_TWO_EXTRA:team_two_extra,
            
            self.COLUMN_DATE:date,
            self.COLUMNS_LAWYERS_TEAMS:lawyers_teams,
            self.COLUMNS_LAWYERS:lawyers,
            self.COLUMNS_TEXT:text,
        }
        return columns
        
        

