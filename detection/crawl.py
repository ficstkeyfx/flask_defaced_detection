import undetected_chromedriver as uc
import os
class Crawl:
    def __init__(self):
        self.driver = uc.Chrome(headless=True,use_subprocess=False)
    
    def crawl_data(self, url):
        self.driver.get(url)
        self.filename = f'{url.replace("/","_").replace(".","_").replace(":","_")}'
        el = self.driver.find_element('tag name','html')
        with open("detection/text/" + self.filename + ".txt",'w', encoding='utf-8') as file:
            file.write(el.text) 
        with open("detection/html/" + self.filename+'.html','w', encoding='utf-8') as file:
            file.write(self.driver.page_source)
        self.driver.save_screenshot("detection/images/" + self.filename +'.png')

if(__name__ == '__main__'):
    crawl = Crawl()
    crawl.crawl_data("https://www.google.com/")
    
