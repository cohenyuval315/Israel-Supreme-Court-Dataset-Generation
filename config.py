

class Config:
    ALL_DATA_DIR_NAME = "data" # the data directory in this current path , it will be created if u dont have
    EACH_QUERY_FILES_DIR_NAME = "pdfs" # for each query it will create a folder and put its downloaded files into this folder name
    EACH_QUERY_CSV_FILE_DIR_NAME = "csv" # for each query it will create a folder and in this folder we will keep the proccessed dataframe csv of this query
    CHROMEDRIVER_PATH = "/usr/bin/chromedriver" # your path to chrome
    DOWNLOAD = True
    MAX_FILES_TO_DOWNLOAD_FROM_QUERY = 100 # max of files to download for the chosen query , its doesnt iterate , for the same query if the files already downloaded , it wont redownload, if u put bigger number it just add the files you didnt have
    TEST = True # not asking for input
    OVERRIDE_EXISTING = False
    REDOWNLOAD_EXISITING = False

    QUERY_TEST_INPUT = "דירות"
    QUERIES = [
        "דירות",
        "פלילי",
        "שכר",
        "זכויות",
        "מיסים",
        "נשק",
        "עבודה",
        "חוקים",
        "התעללות",
        "בריאות",
        "רצח",
        "הגנה",
        "עדים",
        "דת",
        "אפליה",
        "יוצרים",
        "שוחד",
        "חוזה",
        "בניה",
        "גניבה",
        "קנס",
        "נהיגה",
        "רשלנות",
        "משפחה",
        "פשיטת-רגל",
        "צו-הרחקה",
        "חקירה",
        "סכסוך",
        "מעצר",
        "מניעה",
        "ערעור",
        "בית-סוהר",
        "מנהלה",
        "שבח",
        "אימוץ",
        "נוער",
    ]
    


config = Config()