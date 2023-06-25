
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
import asyncio

class VerdictQueryScrapper:
    SEARCH_URL = "https://supreme.court.gov.il/Pages/fullsearch.aspx"
    DOWNLOAD_URL = "https://supremedecisions.court.gov.il/"
    DOWNLOAD_TYPES = ['סוג מסמך: פסק-דין','סוג מסמך: החלטה','סוג מסמך: תקצירים','סוג מסמך: צו','סוג מסמך: צו על תנאי','סוג מסמך: צו ביניים','סוג מסמך: פסקי דין באנגלית','סוג מסמך: פד"י']
    def __init__(self,chromedriver_path) -> None:
        self.chromedriver_path = chromedriver_path
        self.download_type = self.DOWNLOAD_TYPES[0]

    async def scrap_for_file_links(self,search_input,file_type="pdf",delay=0) -> list[str]:
        service = webdriver.chrome.service.Service(self.chromedriver_path) # type: ignore
        service.start()
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.SEARCH_URL)
        driver.maximize_window() 
        driver.implicitly_wait(5) 
        frame = driver.find_element(By.ID,"serviceFram")
        driver.switch_to.frame(frame)
        eles = driver.find_elements(By.ID,"freesearch")
        search_button = driver.find_element(By.XPATH,'//*[@id="outer"]/div[2]/div/form/section[1]/div[2]/button')
        search = eles[1]
        search.send_keys(search_input)
        search_button.click()
        results = driver.find_element(By.CLASS_NAME,"results-listing")
        sub_elements = results.find_elements(By.CLASS_NAME,'res-left-wrap')
        judgement_elements = [sub_ele for sub_ele in sub_elements if sub_ele.find_elements(By.TAG_NAME,'span')[4].text == self.download_type]
        pdfs_links = []
        
        for links in judgement_elements:
            for link in links.find_elements(By.TAG_NAME,"a"):
                if link.get_dom_attribute("class") == f"file-link {file_type}-link":
                    pdfs_links.append(self.DOWNLOAD_URL + link.get_dom_attribute("href"))
        await asyncio.sleep(delay)
        driver.quit()
        return pdfs_links

