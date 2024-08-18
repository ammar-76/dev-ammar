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


# Getting the vendor informations
# We will use it to find the number of matches and also to set the Vendor name in the json file look at Line 167
def get_vendor_info(vendors, vendor_id, return_full_object=False):
    for vendor in vendors:
        # Check if the vendor id in the csv matches the vendor id in the json file.
        if vendor['Id'] == vendor_id:
            # If return_full_object is true return the whole object
            if return_full_object:
                return vendor
            # just return vendor name
            else:
                return vendor['Name']
    return None
# We will use this function to set the json file, look at line 165
def number_match(csv_row, json_row, vendorList):
    csv_vendor= csv_row.get('Supplier').lower()
    json_vendor= get_vendor_info(vendorList,json_row.get('VendorId')).lower()
    if csv_vendor != json_vendor:
        return False
    # We will handel any number in the csv_row['Item'] or json_row['Name'] using regular expresstion
    # After that we will compare the numbers 
    num1 = re.search(r'\d+', csv_row['Item'])
    num2 = re.search(r'\d+', json_row['Name'])
    
    if num1 and num2:
        # num1 and num2 will be objects, to extract the number we use .group() 
        if int(num1.group()) == int(num2.group()):
            return True
    return False

# This function will specify the number befor the ply in the Description.
# We will use to set the number of ply in the json file 
def getPly(s):
    matches=re.search(r'(\d+)\s*(ply)', s, re.IGNORECASE)
    if matches:
        size= int(matches[1]) # This will collect the number beside the ply
        if size in (4,6,8): # if the number is one of these numbers return it
            return size
        else:
            return None
    # Example : getply("teakwood 40x40 8ply") => retruned value = 8 


class MatsExporter:
    # selenium initialization
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
            # Convert the csv file to dictionary
            reader= csv.DictReader(csvfile)
            # Make a list of dictionaries
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
            # Excute this code in the terminal return VendorList(); ,"From Mat page" 
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
            # Construct URLs for each vendor and add them to matching_urls list with the current vendor index.
            for vender in vender_ids:
                # https://www.lsscloud.com/Mat/GetMatsByVendor/?vendorId=Vendor_id 
                matching_urls.append(target_url + str(vender))
                print(vender)
                print(3)
            # Loop through each URL in matching_urls
            for url in matching_urls:
                # Click the the URL
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
                # Create the full file path depending on the id of the current vendor
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
                # Convert the Json file to python object
                new_json= json.loads(new_json)
                # Check if the file is Not empty 
                if not new_json:
                    print("new_json is empty, skipping processing.")
                else:
                    for row in self.csv_data:
                        for j in new_json:
                            # Compare by the vlue of the fields or by the id of the item and name (that the purpose of the function)
                            if (j.get('Name') == row.get('Item')) or number_match(row, j, ):
                                VendorId= j.get('VendorId')
                                VendorName= get_vendor_info(self.mat_by_venids, VendorId)
                                height = int(row['height'])
                                width = int(row['width'])
                                # if the height is greater then the width keep it 
                                if height > width:
                                    j['height']= height
                                    j['width']= width
                                # Else reverse them 
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