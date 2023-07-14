
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
    COLUMS_ALEFS = "procedures"
    COLUMN_TEAM_ONE_NAMES = "team_one_names"
    COLUMN_TEAM_TWO_NAMES = "team_two_names"
    COLUMNS_JUDGES_FIRST_NAMES = "judge_first_names"
    COLUMNS_JUDGES_LAST_NAMES = "judge_last_names"
    COLUMNS_JUDGES_GENDERS = "judges_genders"
    COLUMN_TEAM_ONE = "team_one"
    COLUMN_TEAM_TWO = "team_two"
    COLUMN_DATE = "date"
    COLUMNS_LAWYERS_TEAMS = "all_lawyers_teams_names"
    COLUMNS_LAWYERS = "all_lawyers"
    COLUMN_TEAM_ONE_LAWYERS_TEAMS = "team_one_lawyers_teams_names"
    COLUMN_TEAM_ONE_LAWYERS = "team_one_lawyers"
    COLUMN_TEAM_TWO_LAWYERS_TEAMS = "team_two_lawyers_teams_names"
    COLUMN_TEAM_TWO_LAWYERS = "team_two_lawyers"



    COLUMNS_TEXT = "text"
    COLUMNS_END = "end"
    COLUMN_DECISION = "decision"
    COLUMN_DATA = "data"
    
    COLUMN_TEAM_ONE_EXTRA_NAMES = "team_one_extra_names"
    COLUMN_TEAM_ONE_EXTRA = "team_one_extra"
    COLUMN_TEAM_TWO_EXTRA_NAMES = "team_two_extra_names"
    COLUMN_TEAM_TWO_EXTRA = "team_two_extra"

    COLUMNS_ALL_LAWYERS = "teams_lawyers"
    COLUMNS_ALL_LAWYERS_TEAMS = "teams_laywers_names"
    COLUMNS_ALL_LAWYERS_TEAMS_EXTRA = "lawyers_extra"


    csv_columns = []
    def __init__(self,data_dir,query_data_dir,query_processed_data_dir) -> None:
        self.data_dir = data_dir
        self.query_data_dir = query_data_dir
        self.query_processed_data_dir = query_processed_data_dir


    async def area_spliting(self, text:str,id:int):
        verdict_data_divider = "דין-פסק"
        team_versus_divider =  "ד  ג  נ"
        date_verdict_sitting = "הישיבה תאריך"
        date_verdict_sitting2 = "הישיבות תאריכי"
        before_judges_divider = "לפני"
        lawyers_prefix = "בשם"

        verdict_data_divider_index = await find_text_first_index_in_list(text.split("\n"),verdict_data_divider)
        if not verdict_data_divider_index:
            return False
        
        # data of the verdict
        verdict_data = "\n".join(text.split("\n")[:verdict_data_divider_index]) 

        # date_splitter = verdict_data.split(date_verdict_sitting)
        # if len(date_splitter) == 1:
        #     lawyers_start_index = await find_text_first_index_in_list(date_splitter[0].split("\n"),lawyers_prefix)
        #     verdict_lawyer_area = "\n".join(date_splitter[0].split("\n")[lawyers_start_index:])
        #     verdict_teams_data = "\n".join(date_splitter[0].split("\n")[:lawyers_start_index])   
        #     verdict_date_area = "None"         
        # else:
        #     verdict_teams_data = date_splitter[0]
        #     verdict_lawyer_area = date_splitter[1]
        #     date_index = len(verdict_teams_data.split("\n"))-1
        #     verdict_date_area = verdict_teams_data.split("\n")[date_index]
        #     verdict_teams_data = "\n".join(verdict_teams_data.split("\n")[:date_index])



        #team_splitter = verdict_teams_data.split(team_versus_divider)
        team_splitter = verdict_data.split(team_versus_divider)


        verdict_team_2_lawyers_date_area = team_splitter[1]


        # Team One and Judges Areas Mapping 
        verdict_data_with_team1 = team_splitter[0]
        title_index = 0
        verdict_title_area = verdict_data_with_team1.split("\n")[title_index]
        verdict_data_with_team1 = "\n".join(verdict_data_with_team1.split("\n")[title_index + 1:])
        before_judges_divider = await find_text_first_index_in_list(verdict_data_with_team1.split("\n"),before_judges_divider)
        if not before_judges_divider:
            return False
        judges_and_team1 = "\n".join(verdict_data_with_team1.split("\n")[before_judges_divider:])
        verdict_alefs_area = "\n".join(verdict_data_with_team1.split("\n")[:before_judges_divider])
        judges_and_team1_splitter = judges_and_team1.split("\n")
        judges_end_index = -1
        for i,line in enumerate(judges_and_team1_splitter):
            if "כבוד" in line and i > 0:
                pass
            else:
                if i > 0:
                    judges_end_index = i
                    break
        if judges_end_index == -1:
            return False
        judges_area = judges_and_team1_splitter[:judges_end_index]
        team1_area = judges_and_team1_splitter[judges_end_index:]
        
        verdict_judges_area = "\n".join(judges_area)
        verdict_team_1_area = "\n".join(team1_area)        

        lawyers_start_index = await find_text_first_index_in_list(verdict_team_2_lawyers_date_area.split("\n"),lawyers_prefix)

        verdict_lawyers_area = "\n".join(verdict_team_2_lawyers_date_area.split("\n")[lawyers_start_index:])
        verdict_teams_2_date_area = "\n".join(verdict_team_2_lawyers_date_area.split("\n")[:lawyers_start_index])



        date_index = -1
        for i,line in enumerate(verdict_teams_2_date_area.split("\n")):
            if date_verdict_sitting in line:
                date_index = i
            if date_verdict_sitting2 in line:
                date_index = i
            
        
        if date_index == -1:
            verdict_date_area = None
            verdict_team_2_area = verdict_teams_2_date_area
        else:
            temp = verdict_teams_2_date_area.split("\n")
            verdict_date_area = temp[date_index]
            del temp[date_index]
            verdict_team_2_area = "\n".join(temp[:date_index - 1])


        verdict_areas = (verdict_title_area, 
                         verdict_alefs_area,
                         verdict_judges_area,
                         verdict_team_1_area,
                         verdict_team_2_area,
                         verdict_date_area,
                         verdict_lawyers_area,
                         text
                         )
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

    async def process_verdict_date(self,date_area,text:str): #done
        start_date = "("
        end_date = ")"
        start_index = -1
        end_index = -1
        if date_area is not None:     
            for i,s in enumerate(date_area):
                if s is start_date:
                    start_index = i           
                if s is end_date:
                    end_index = i
            if start_index == -1 or end_index == -1:
                pass
            else:
                d = date_area[start_index+1:end_index].strip()
                return d
        else:
            text_lines = [line for line in text.split("\n")]
            for line in reversed(text_lines):
                date_pattern = r'(?:\d{1,2}\.){2}\d{4}' 
                dates = re.findall(date_pattern, line)
                if dates:
                    return dates[-1]  
        return None
        
                


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

    async def process_lawyers(self,text:str):
        prefix = "בשם"
        colon =  ":"
        lawyer_prefix = 'ד"עו'
        words = text.split(" ")
        words.append(" ")
        lawyers_indexes = []
        s = 0

        ws = []
        
        for i, word in enumerate(words):
            if prefix in word and "\n" in word:
                w1 = word.split("\n")[0]
                w2 = word.split("\n")[1]
                ws.append(w1)
                ws.append("\n")
                ws.append(w2)  
            else: 
                if "\n" in word:
                    w1 = word.split("\n")[0]
                    w2 = word.split("\n")[1]
                    ws.append(w1)
                    ws.append("\n")
                    ws.append(w2)  
                else:
                    ws.append(word)
        ws = [w for w in ws if len(w) > 0]
        words = ws
        for i, word in enumerate(words):
            if lawyer_prefix in word:
                lawyers_indexes.append((i-2,i + 1))
                s = i + 1 

        start = 0
        missing_indexes = []
        for i in range(len(lawyers_indexes)-1):
            start = lawyers_indexes[i][1]
            finish = lawyers_indexes[i+1][0]
            missing_indexes.append((start, finish))
        if lawyers_indexes[0][0] != 0:
            missing_indexes.append((0,lawyers_indexes[0][0]))
        missing_indexes.append((lawyers_indexes[len(lawyers_indexes) - 1][1], len(words) - 1))
        missing_indexes = [index for index in missing_indexes if index[0] != index[1]]
        
        indexes = lawyers_indexes + missing_indexes
        indexes.sort(key=lambda key:key[0])

        current_lst = []
        result = {}
        for index in indexes:
            if index in missing_indexes:
                s = index[0]
                e = index[1]
                title = " ".join(words[s:e])
                title = remove_extra_spaces(title)
                result[title] = current_lst
                current_lst = []
            else:
                s = index[0]
                e = index[1]
                w = words[s:e]
                lst = [l for l in w]
                lst = [l.replace(":","") for l in words[s:e]]
                lst = [l.replace(";","") for l in lst]
                lst = [w.strip() for w in lst]
                lst = [w for w in lst if len(w) > 0]
                name = " ".join(lst)                
                current_lst.append(name)
        return result
            


    async def process_team(self,text:str):
        # print(text)
        colon =  ":"
        words = text.split(" ")
        words.append(" ")
        lst_indexes = []
        s = 0

        ws = []
        for i, word in enumerate(words):
            if "." in word or "\n" in word or ":" in word:
                if "." in word:
                    w = word.split(".")                  
                    w1 = w[0]
                    w2 = w[1]
                    if w1 == "":
                        w1 = "."
                    else: 
                        if w2 == "":
                            w2 = "."
                    ws.append(w1)
                    ws.append(w2)  
                if "\n" in word:
                    w1 = word.split("\n")[0]
                    w2 = word.split("\n")[1]
                    ws.append(w1)
                    ws.append(w2)  
                if ":" in word:
                    w = word.split(":")                  
                    w1 = w[0]
                    w2 = w[1]
                    if w1.strip() == "":
                        w1 = ":"
                    else: 
                        if w2.strip() == "":
                            w2 = ":"
                    ws.append(w1)
                    ws.append(w2)  
            else:
                ws.append(word)


        ws = [w for w in ws if len(w) > 0]
        words = ws

        # print(words)
        s = 0
        for i, word in enumerate(words):
            if ":" in word:
                s = i + 1 
            if " " == word:
                lst_indexes.append((s,i + 1))
        # print(lst_indexes)
        for i in lst_indexes:
            # print(" ".join(words[i[0]:i[1]]))
            pass

        start = 0
        missing_indexes = []
        for i in range(len(lst_indexes)-1):
            start = lst_indexes[i][1]
            finish = lst_indexes[i+1][0]
            missing_indexes.append((start, finish))
        if lst_indexes[0][0] != 0:
            missing_indexes.append((0,lst_indexes[0][0]))
        missing_indexes.append((lst_indexes[len(lst_indexes) - 1][1], len(words) - 1))
        missing_indexes = [index for index in missing_indexes if index[0] != index[1]]
        
        indexes = lst_indexes + missing_indexes
        indexes.sort(key=lambda key:key[0])

        current_lst = []
        result = {}
        for index in indexes:
            if index in missing_indexes:
                s = index[0]
                e = index[1]
                title = " ".join(words[s:e])
                result[title] = current_lst
                current_lst = []
            else:
                s = index[0]
                e = index[1]
                lst = [l.replace(":","") for l in words[s:e]]
                lst = [l.replace(";","") for l in lst]
                lst = [w.strip() for w in lst]
                lst = [w for w in lst if len(w) > 0]
                name = " ".join(lst)                
                current_lst.append(name)

        return result
          

    async def process_verdict_lawyers(self,lawyers:str): # done
        result_dict = await self.process_lawyers(lawyers)
        keys = list(result_dict.keys())
        values = []
        for key in result_dict.keys():
            lst = result_dict[key]
            values.append(lst)    
        return keys,values

    async def process_verdict_text(self,text:str): # done
        return text

        

    async def process_verdict_end(self,end:str): # None
        # print("end=",end)
        return end

    async def process_verdict_decision(self,decision:str):
        return decision
    

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
    
    async def process_list_to_str(self,lst:list,char="|"):
        encoded_string = char.join(lst)
        return encoded_string
    

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
        

    async def process_nested_list_to_str(self,lst:list):
        new_list = []
        for l in lst:
            l_string = await self.process_list_to_str(l)
            new_list.append(l_string)
        return await self.process_list_to_str(new_list,char="@")
        


    async def process_dict_like_text(self,text:str):
        titles = []
        data = []
        not_found_title_start = True
        t = []
        for i,line in enumerate(text.split("\n")):    
            if ":" in line:
                not_found_title_start = False
                titles.append(line.split(":")[-1].strip())
                data.append(line.split(":")[0].strip() +"@")
            else:
                if not_found_title_start:
                    t.append(line)
                else:
                    data.append(line)

        
        data = [d.strip() for d in data if len(d.strip()) > 0]

        list_pattern = r"\.\s{1,2}\d{1,2}"
        

    
        current_list = []

        extra = []
        last_index = 0
        for i, line in enumerate(reversed(data)):
            if re.search(list_pattern,line) or "@" in line:
                break
            else:
                extra.append(line)
                last_index += 1

        for i, line in enumerate(data):
            if "@" in line:
                data[i] = line.split("@")[0].strip()

        
        
        # print("before:")
        # print(data)
        data = data[:len(data) - last_index]

        # print("after:")
        # print(data)
        # print("extra:")
        # print(extra)

        numbers_lists = []
        plain_text_list = []

        for i in range(len(data)):
            line = data[i]
            # print(line)
            search = re.search(list_pattern,line)
            if search:
                numbers_lists.append((i,line))
            else:
                try:
                    search1 = re.findall(list_pattern,data[i - 1])
                    search2 = re.findall(list_pattern,data[i + 1])
                    n1 = [int(match.strip(". ")) for match in search1]
                    n2 = [int(match.strip(". ")) for match in search2]
                    if n1[0] + 1 == n2[0]:
                        numbers_lists[len(numbers_lists) - 1] = (numbers_lists[len(numbers_lists) - 1][0] ,line + " " +numbers_lists[len(numbers_lists) - 1][1])
                        continue
                except:
                    pass
                plain_text_list.append((i,line))

        number_lists_result = []
        current_list = []
        
        for item in numbers_lists:
            if item[1].endswith('. 1'):
                if current_list:
                    number_lists_result.append(current_list)
                current_list = [item]
            else:
                current_list.append(item)

        if current_list:
            number_lists_result.append(current_list)


        plain_text_result = []
        current_list = []

        for item in plain_text_list:
            n_value, plain_text = item
            if not current_list or n_value != current_list[-1][0] + 1:
                if current_list:
                    plain_text_result.append(current_list)
                current_list = []
            current_list.append(item)

    
        if current_list:
            plain_text_result.append(current_list)


        results = number_lists_result + plain_text_result
        results = sorted(results,key = lambda lst: lst[0][0]) 
        total_list = []
        for lst in results:
            total_list.append([item[1] for item in lst])

        if len(total_list) != len(titles):
            return False
        
        return titles,total_list,extra

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

        
        # print(verdict_judges_area,"\n")
        # print(verdict_team_1_area,"\n")
        # print(verdict_team_2_area,"\n")
        # print(verdict_lawyer_area,"\n")
        
        title = await self.process_verdict_title(verdict_title_area)
        alefs = await self.process_verdict_alefs(verdict_alefs_area)
        date = await self.process_verdict_date(verdict_date_area,text)


        judges_first_names,judges_last_names,judges_genders = await self.process_verdict_judges(verdict_judges_area)

        t1= await self.process_dict_like_text(verdict_team_1_area)
        t2 = await self.process_dict_like_text(verdict_team_2_area)
        if t1 is False or t2 is False:
            return False
        team_one_names,team_one,team_one_extra = t1
        
        team_two_names,team_two,team_two_extra = t2

        # t_law = await self.process_dict_like_text(verdict_lawyer_area)
        # if t_law is False:
        #     return False
        
        # team_lawyers_teams_names,teams_lawyers,lawyers_extra = t_law
        
        

        # team_one_names, team_one,team_one_extra_names,team_one_extra = await self.process_verdict_team(verdict_team_1_area)
        # team_two_names,team_two,team_two_extra_names,team_two_extra = await self.process_verdict_team(verdict_team_2_area)
        lawyers_teams,lawyers = await self.process_verdict_lawyers(verdict_lawyer_area)
        
        # res = await self.process_team(verdict_team_1_area)
        # print(res)


        # print(team_one)
        # print(team_one_extra_names)
        # print(team_one_extra)
        
        # print(team_two)
        # print(team_two_extra)
        # print(team_two_extra_names)
        # print(verdict_lawyer_area)
        # print("team:",lawyers_teams)
        # print("lawyers:", lawyers)
        # for i in lawyers_teams:
        #     if i in remove_extra_spaces(text):
        #         print("in text")
        #     else:
        #         print("not in text")

        team_one_lawyers_team_name = []
        team_two_lawyers_team_name = []
        team_one_lawyers = []
        team_two_lawyers = []
        
        for i,team in enumerate(lawyers_teams):
            team_lawyers = lawyers[i]
            for t1 in team_one_names:
                if t1[1:5] in team:
                    team_one_lawyers_team_name.append(team)
                    team_one_lawyers.append(team_lawyers)
                    continue
            for t2 in team_two_names:
                if t2[1:5] in team:
                    team_two_lawyers_team_name.append(team)
                    team_two_lawyers.append(team_lawyers)
                    continue            
        # print("LAWYERS_TEAMS:",lawyers_teams)
        # print("LAWYERS:",lawyers)
        # print("1 NAMES:",team_one_lawyers_team_name)
        # print("2 NAMES:",team_two_lawyers_team_name)
        # print("1_TEAMS:",team_one_lawyers)
        # print("2_TEAMS:",team_two_lawyers)        

        

        team_one_lawyers_team_name = await self.process_list_to_str(team_one_lawyers_team_name)
        team_two_lawyers_team_name = await self.process_list_to_str(team_two_lawyers_team_name)
        team_one_lawyers = await self.process_nested_list_to_str(team_one_lawyers)
        team_two_lawyers = await self.process_nested_list_to_str(team_two_lawyers)


        
        team_one_names = await self.process_list_to_str(team_one_names)
        team_two_names = await self.process_list_to_str(team_two_names)
        lawyers_teams = await self.process_list_to_str(lawyers_teams)
        lawyers =  await self.process_nested_list_to_str(lawyers)
        team_one = await self.process_nested_list_to_str(team_one)
        team_two = await self.process_nested_list_to_str(team_two)
        team_one_extra = "\n".join(team_one_extra)
        team_two_extra = "\n".join(team_two_extra)
        alefs = await self.process_list_to_str(alefs)
        judges_first_names = await self.process_list_to_str(judges_first_names)
        judges_last_names = await self.process_list_to_str(judges_last_names)
        judges_genders = await self.process_list_to_str(judges_genders)

        # print(verdict_team_2_area)
        




        columns = {
            self.COLUMN_TITLE :title,
            self.COLUMS_ALEFS: alefs,
            self.COLUMNS_JUDGES_FIRST_NAMES:judges_first_names,
            self.COLUMNS_JUDGES_LAST_NAMES:judges_last_names,
            self.COLUMNS_JUDGES_GENDERS:judges_genders,

            self.COLUMN_TEAM_ONE_NAMES:team_one_names,
            self.COLUMN_TEAM_ONE:team_one,
            self.COLUMN_TEAM_ONE_EXTRA:team_one_extra,
            
            self.COLUMN_TEAM_TWO_NAMES:team_two_names,
            self.COLUMN_TEAM_TWO:team_two,
            self.COLUMN_TEAM_TWO_EXTRA:team_two_extra,

            self.COLUMN_TEAM_ONE_LAWYERS_TEAMS:team_one_lawyers_team_name,
            self.COLUMN_TEAM_ONE_LAWYERS:team_one_lawyers,
            self.COLUMN_TEAM_TWO_LAWYERS_TEAMS:team_two_lawyers_team_name,
            self.COLUMN_TEAM_TWO_LAWYERS:team_two_lawyers,

            self.COLUMN_DATE:date,
            self.COLUMNS_LAWYERS_TEAMS:lawyers_teams,
            self.COLUMNS_LAWYERS:lawyers,
            self.COLUMNS_TEXT:text,

            # self.COLUMNS_ALL_LAWYERS_TEAMS:team_lawyers_teams_names,
            # self.COLUMNS_ALL_LAWYERS_TEAMS_EXTRA:lawyers_extra,
        }
        return columns
        
        

