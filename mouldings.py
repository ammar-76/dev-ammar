import json
import os
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# from pywinauto import mouse
import datetime
from json2csv import json_to_csv_file

class MouldingsExporter:
    def __init__(self, driver=None):
        if driver is None:
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            self.driver = webdriver.Chrome(service=Service(
                ChromeDriverManager().install()), options=chrome_options)
        else:
            self.driver = driver

    def export_mouldings(self):
        try:
            # to run download_har() function
            self.download_har()
        except Exception as e:
            print(f"Export Mouldings Error: {e}")

    def download_har(self):
        try:
            # Navigate to the specified URL
            self.driver.get('https://www.lsscloud.com/Moulding')
            time.sleep(3)
            # array conatin IDs come from moulding page
            vendor_ids = []
            # execute secript on google console to get array contain all moulding ids
            vendor_list = self.driver.execute_script("return VendorList();")
            # add ids info array
            self.vendor_dict={}
            for vendor in vendor_list:
                vendor_ids.append(vendor["Id"])
                self.vendor_dict[vendor["Id"]] = vendor["Name"]

            # after the array get all ids => run secript function
            self.run_script(vendor_ids)

        except Exception as e:
            print(f"Download HAR Error: {e}")

    def run_script(self, vendor_ids):
        # vendor_ids all matches ids
        try:
            # target URL of mouldings
            target_url = "https://www.lsscloud.com/Moulding/GetDetailedMouldingsByVendor/?VendorId="
            # array contain URL to moulding +id of each vender
            matching_urls = []
            # store full URL of each vender ids
            for vendor_id in vendor_ids:
                matching_urls.append(target_url + str(vendor_id))
            # open each URL we have made above
            for url in matching_urls:
                self.driver.get(url)
                print(f"Visited: {url}")
                time.sleep(5)

                # mouse.click(coords=(430, 118))
                time.sleep(2)
                # save current page
                # pyautogui.hotkey('ctrl', 's')
                # time.sleep(3)

                # mouse.click(coords=(553, 510))
                # time.sleep(2)

                # directory where main.py is located
                currentPath = os.path.dirname(__file__)

                # path to desired folder
                path_to_forlder = currentPath + "\output"
                os.makedirs(path_to_forlder, exist_ok=True)
                # time stamp to label file
                # timestamp = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
                # name of file will saved
                curr_vendor= int(url.split('=')[1])
                file_name = f"mouldings_{curr_vendor}_{self.vendor_dict[curr_vendor]}.json"

                # Create the full file path by joining the folder path with the file name
                file_path = os.path.join(path_to_forlder, file_name)
                # Write the full file path into the save dialog
                # pyautogui.write(file_path)

                string_result= self.driver.execute_script("return document.querySelector('*').innerText")
                json_result= json.loads(string_result)
                json_result= [self.transform(m, curr_vendor) for m in json_result]
                json_output= json.dumps(json_result, indent=1)
                with open(file_path, 'w') as json_output_file:
                    json_output_file.write(json_output)
                json_to_csv_file(file_path)
                # time.sleep(3)
                # click the "Save" button
                # mouse.click(coords=(806, 508))
                # Pause the script for 3 seconds to allow the save operation to complete
                # time.sleep(3)

            print("Script completed successfully.")
        except Exception as e:
            print(f"Error: {e}")

    # input string is the id 
    def strip_starting_alphabets(self, input_string):
        index = 0
        while index < len(input_string) and input_string[index].isalpha():
            index += 1
        return input_string[index:]

    def transform(self, input_moulding, vendorId):
        '''takes a moulding and modifies it to return the desired format'''

        new_obj = {
        "id": input_moulding.get("Name"),
        "upc": input_moulding.get("UPC"),
        "description": input_moulding.get("Description"),
        "width": input_moulding.get("WidthInInches"),
        "chop": input_moulding.get("ChopCost"),
        "join": input_moulding.get("JoinCost"),
        "length": input_moulding.get("LengthCost"),
        "vendor": self.vendor_dict[vendorId]
        }
        
        new_obj["id"]= self.strip_starting_alphabets(new_obj["id"])

        return new_obj



if __name__ == "__main__":
    exporter = MouldingsExporter()
    exporter.export_mouldings()