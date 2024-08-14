import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pyautogui
from pywinauto import mouse
import json


class InvoiceExporter:
    def __init__(self, driver=None):
        if driver is None:
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)

            chrome_manager= ChromeDriverManager().install()
            driver_path= os.path.join(os.path.dirname(chrome_manager), "chromedriver.exe")

            self.driver = webdriver.Chrome(service=Service(
                driver_path), options=chrome_options)
        else:
            self.driver = driver
    def get_json(self):
        # Select all the elements on the page. 
        string_result= self.driver.execute_script("return document.querySelector('*').innerText")
        # Change the JSON type to dictionary 
        json_result= json.loads(string_result)
        return json_result
    def save_json(self,file_path, json_data):
        # Convert the dictionary back to JSON , indent = 1  order lines Verticaly
        json_output= json.dumps(json_data, indent=1)
        # Open file_path and write the JSON into it , which is the innerText for the page 
        with open(file_path, 'w') as json_output_file:
            json_output_file.write(json_output)

    def export_invoices(self):
        try:
            time.sleep(5)
            # Get the URL using selenium. 
            self.driver.get('https://www.lsscloud.com/Invoice/BrowseInvoice')

            # Click on '50' button to show more invoices.
            click50_button = self.driver.find_element(
                # Selecting the third Button inside the second inner div inside body-content.
                By.XPATH, '//*[@id="body-content"]/div[1]/div[1]/div/button[3]')
            click50_button.click()

            time.sleep(3)

            # Get the invoice ids from the html doc and make a loop.
            a_elements = self.driver.find_elements(
            # Select any anchor that has the class name btn-primary.
                By.XPATH, "//a[contains(@class, 'btn-primary')]")

            id_list = set()

            for a in a_elements:
                # Extarcting the URL in the anchor.
                href = a.get_attribute("href")
                # Get the last element in the URL which is the id.
                id_number = href.split('/')[-1]
                id_list.add(id_number)

            id_set = set(id_list)
            # List contain's All the ids.
            unique_id_list = list(id_set)

            for id_number in unique_id_list:
                print("ID number:", id_number)

                base_url = 'https://www.lsscloud.com/Invoice/GetInvoice/'
                # the full URL with the id in the end
                new_url = f"{base_url}{id_number}"

                self.driver.get(new_url)

                time.sleep(2)

                # mouse.click(coords=(533, 33))

                # time.sleep(2)

                # pyautogui.hotkey('ctrl', 's')
                # time.sleep(5)

                # mouse.click(coords=(553, 510))
                # time.sleep(2)

                json_from_page= self.get_json()
                # Adding the ids to the folder. 
                folder_path = os.path.abspath('./InvoiceJsonFiles')
                os.makedirs(folder_path, exist_ok=True)
                # id.json 
                file_name = f"{id_number}.json"
                # Combining the folder_path and file_name to be in one path.
                # ./InvoiceJsonFiles/id.json
                full_path = os.path.join(folder_path, file_name)
                self.save_json(full_path, json_from_page)
                # pyautogui.write(full_path)
                # time.sleep(3)

                # pyautogui.press('enter')

                # time.sleep(2)

                # mouse.click(coords=(806, 508))

                time.sleep(3)
                
            

        except Exception as e:
            print(f"Error occurred: {e}")


        def get_invoice_payment_file(id_set):
            try:
                invoice_dir = '/Users/Yusra/Desktop/InvoiceJsonFiles'
                payment_dir = '/Users/Yusra/Desktop/InvoicesPdf'

                json_files = {}
                # Loop through all the files inside this path {/Users/Yusra/Desktop/InvoiceJsonFiles}.
                for filename in os.listdir(invoice_dir):
                    # Allocating all the json files.
                    if filename.endswith('.json'):
                        # Add the invoice_dir and payment_dir prior every file name 
                        # Baisaclly we are creating two versions of the same file
                        invoice_file_path = os.path.join(invoice_dir, filename)
                        payment_file_path = os.path.join(payment_dir, filename)
                        print("invoice"+invoice_file_path)
                        print("payment"+payment_file_path)


            except Exception as e:
                print(f"Error occurred: {e}")



            




if __name__ == "__main__":
    invoice_scraper = InvoiceExporter()
    invoice_scraper.export_invoices()
