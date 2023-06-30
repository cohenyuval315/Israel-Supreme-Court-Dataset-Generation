from nltk.corpus import stopwords
import math
from collections import Counter
import enum
import nltk
nltk.download('stopwords')
import regex as re
from utils import remove_extra_spaces

class Sentiment(enum.Enum):
    POSITIVE = "positive"
    NETURAL = "netural"
    NEGATIVE = "negative"
    MIXED = "mixed"


class VerdictHebrewNLP:
    COLUMNS_TAGS = "tags"
    COLUMNS_SENTIMENT = "sentiment"
    COLUMNS_TEXT_BAG_OF_WORDS = "text_bag"
    COLUMNS_BAG_OF_WORDS = "bag"    

    VERDICT_POSITIVE_WORDS = [           
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

    VERDICT_NEGATIVE_WORDS = [
        "לדחות",
        "נדחה",
        "נדחת",
        "לסרב" ,    
        "דוחה",
        "מסרבים",
        "מסרבת",
        "מסרב" ,     
    ]


    def __init__(self) -> None:
        self.hebrew_stopwords = self.read_hebrew_stop_words()
        self.idf_dict = {}
        self.idf_files = []

    def read_hebrew_stop_words(self):
        itdk_stopwords = stopwords.words("hebrew")
        total_stopwords = []
        txt_stopwords = []
        with open("./heb_stopwords.txt") as f:
            for line in f:
                txt_stopwords.append(f.readline())
        txt_stopwords = txt_stopwords[:len(txt_stopwords)- 1]
        txt_stopwords = [word.split("\n")[0].strip() for word in txt_stopwords]
        total_stopwords.extend(txt_stopwords)
        total_stopwords.extend(itdk_stopwords)
        total_stopwords = list(set(total_stopwords))
        return total_stopwords
    
    async def get_sentiment(self,text):
        return Sentiment.NETURAL


    async def get_bag_of_words(self,text:str):
        pattern = r'[^א-ת\s-]'
        cleaned_text = re.sub(pattern, ' ', text)
        words = cleaned_text.split(' ')
        words = [await remove_extra_spaces(word) for word in words if len(word) > 0]
        words = [word.strip() for word in words]
        words = [word for word in words if word not in self.hebrew_stopwords]
        word_counts = Counter(words)
        return word_counts


    async def compute_idf(self,file_name:str, bag_dict:Counter):
        if file_name in self.idf_files:
            return
        self.idf_files.append(file_name)
        words = list(bag_dict.keys())
        for word in words:
            if not self.idf_dict.get(word):
                self.idf_dict.update({word:0})
        for word,count in bag_dict.items():
            self.idf_dict[word] += count            


    async def compute_tf_idf(self,tf_bag_dict:dict):
        tf_idf_dict = {}
        for word,count in tf_bag_dict.items():
            tf_idf_dict[word] = count * self.idf_dict[word]
        return tf_idf_dict

    async def compute_tf(self,bag_dict:dict): # self freqs = term freq =  tf
        total_num_words = 0
        for word,count in bag_dict.items():
            total_num_words += count
        tf_bag = bag_dict.copy()
        for word,count in tf_bag.items():
            tf_bag[word] = float(count) / float(total_num_words)
        return tf_bag


    async def process_bag(self,file_name:str,bag_dict):
        await self.compute_idf(file_name,bag_dict) # add to total documents
    
    async def single_process_bag(self,file_name:str,bag_dict):
        await self.compute_idf(file_name,bag_dict) # add to total documents
        tf_bag_dict = await self.compute_tf(bag_dict)
        tf_idf_dict = await self.compute_tf_idf(tf_bag_dict)
        return tf_bag_dict,tf_idf_dict        
    
    async def get_tags(self,td_idf_bag:dict):
        sorted_values = dict(sorted(td_idf_bag.items(), key=lambda item: item[1]))
        tags = []
        scores = []
        for tag,value in sorted_values.items():
            tags.append(tag)
            scores.append(value)
        return tags,scores
