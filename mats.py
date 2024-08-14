import datetime
import os
import time
import json
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pywinauto import mouse
from urllib.parse import urlparse, parse_qs
import csv
import re

def get_vendor_info(vendors, vendor_id, return_full_object=False):
    for vendor in vendors:
        if vendor['Id'] == vendor_id:
            if return_full_object:
                return vendor
            else:
                return vendor['Name']
    return None

def number_match(csv_row, json_row, vendorList):
    csv_vendor= csv_row.get('Supplier').lower()
    json_vendor= get_vendor_info(vendorList,json_row.get('VendorId')).lower()
    if csv_vendor != json_vendor:
        return False
     
    num1 = re.search(r'\d+', csv_row['Item'])
    num2 = re.search(r'\d+', json_row['Name'])
    
    if num1 and num2:
        if int(num1.group()) == int(num2.group()):
            return True
    return False

def getPly(s):
    matches=re.search(r'(\d+)\s*(ply)', s, re.IGNORECASE)
    if matches:
        size= int(matches[1])
        if size in (4,6,8):
            return size
        else:
            return None


class MatsExporter:
    def __init__(self, driver=None):
        if driver is None:
            chrome_options = Options()
            # chrome_options.add_experimental_option("detach", True)
            chrome_manager= ChromeDriverManager().install()
            driver_path= os.path.join(os.path.dirname(chrome_manager), "chromedriver.exe")
            self.driver = webdriver.Chrome(service=Service(driver_path
                ), options=chrome_options)
        else:
            self.driver = driver
        

        with open('data_split_swap.csv','r', encoding='latin1') as csvfile:
            reader= csv.DictReader(csvfile)
            self.csv_data= list(reader)
            # for row in reader:
            #     self.lookup_map[row.get('Item')]= row

    def export_mats(self):
        try:
            self.download_har()
        except Exception as e:
            print(f"Export Mats Error: {e}")

    def download_har(self):
        try:
            self.driver.get('https://www.lsscloud.com/Mat')
            time.sleep(3)

            # Array to hold ids of vendors by mats
            vender_ids = []

            # Return list of all vendor ids belong to mats
            self.mat_by_venids = self.driver.execute_script("return VendorList();")

            # Loop to search for id from mat_by_venIds and add it to array venderIds
            for vendor in self.mat_by_venids:
                vender_ids.append(vendor['Id'])

            # after the array of ids complete run the function:
            self.run_script(vender_ids)

        except Exception as e:
            print(f"Download HAR Error: {e}")

    def run_script(self, vender_ids):
        try:
            # Base URL for retrieving mats by vendor
            target_url = "https://www.lsscloud.com/Mat/GetMatsByVendor/?vendorId="
            # Counter to keep track of the current vendor index
            counter = 0
            # List to store URLs constructed for each vendor
            matching_urls = []
            # Construct URLs for each vendor and add them to matching_urls list
            for vender in vender_ids:
                matching_urls.append(target_url + str(vender))
                print(vender)
                print(3)
             # Loop through each URL in matching_urls
            for url in matching_urls:
                # Navigate to the URL
                self.driver.get(url)
                print(f"Visited: {url}")
                time.sleep(5)

                mouse.click(coords=(430, 118))
                time.sleep(2)
                # to open the save dialog
                pyautogui.hotkey('ctrl', 's')
                time.sleep(3)
                # the save path input field
                mouse.click(coords=(553, 510))
                time.sleep(2)

               # This gives you the directory where main.py is located
                currentpath = os.path.dirname(__file__)
               # path to desired folder
                path_to_folder = os.path.join(currentpath, "output")
               # Create the full file path
                file_name = f"mats_{vender_ids[counter]}.json"
                file_path = os.path.join(path_to_folder, file_name)
                # Write the full file path into the save dialog
                pyautogui.write(file_path)

                time.sleep(3)
                # click the 'Save' button
                mouse.click(coords=(806, 508))
                time.sleep(3)
                # Increment the counter for the next vendor
                counter += 1

                new_json= open(file_path, 'r').read()
                new_json= json.loads(new_json)
                if not new_json:
                    print("new_json is empty, skipping processing.")
                else:
                    for row in self.csv_data:
                        for j in new_json:
                            if (j.get('Name') == row.get('Item')) or number_match(row, j, ):
                                VendorId= j.get('VendorId')
                                VendorName= get_vendor_info(self.mat_by_venids, VendorId)
                                height = int(row['height'])
                                width = int(row['width'])
                                if height> width:
                                    j['height']= height
                                    j['width']= width
                                else:
                                    j['height']= width
                                    j['width']= height


                        j['vendor']= VendorName
                        j['ply']= getPly(row.get('Description', ''))
                        j['id']= j["Name"]
                        j["upc"]= j["UPC"]
                        j["description"]= j["Description"]
                        j["cost"]= j["Cost"]
                        j["oversize"]= j["Oversize"]
                        del j['Id']
                        del j['UPC']
                        del j['Description']
                        del j['Cost']
                        del j['Oversize']
                    

                    file_name = f"updated_mats_{vender_ids[counter]}.json"
                    file_path = os.path.join(path_to_folder, file_name)
                    with open(file_path, 'w') as output:
                        output.write(json.dumps(new_json, indent=1))

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    exporter = MatsExporter()
    exporter.export_mats()