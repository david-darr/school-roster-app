# === File: sync.py ===
# Contains sync_from_humanity to gather shifts

import time
import json
import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from models import School, normalize_name

def sync_from_humanity(schools):
    shift_data = []
    common_sports = {"soccer", "basketball", "yoga", "football", "volleyball", "tennis", "track", "running", "chess"}

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)

        driver.get("https://www.humanity.com/app/")
        time.sleep(2)
        driver.find_element(By.ID, "email").send_keys("<your_email>")
        driver.find_element(By.ID, "password").send_keys("<your_password>")
        driver.find_element(By.NAME, "login").click()
        time.sleep(2)

        driver.get("https://richardburke1.humanity.com/app/schedule/list/month/employee/employee/18%2c3%2c2025/")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        shift_rows = driver.find_elements(By.CSS_SELECTOR, "tr.shiftrow")

        def extract_date(class_list):
            for cls in class_list:
                if cls.startswith("tl_"):
                    try:
                        parts = cls.replace("tl_", "").split("__")
                        date_str = parts[0] + " " + parts[1]
                        date_obj = datetime.datetime.strptime(date_str, "%b_%d %Y")
                        return date_obj.strftime("%Y-%m-%d")
                    except:
                        return None
            return None

        def is_valid_address(text):
            address_pattern = r"\d+\s+\w+(\s+\w+)*\s+(St|Ave|Rd|Blvd|Dr|Ln|Way|Ct|Circle|Pl|Terrace|Pkwy|Highway|Hwy|Loop|Square|Sq|Trail|Trl|Drive|Street|Avenue|Road|Boulevard|Place|Lane|Way|Court|Parkway|Circle|Terrace)\b"
            return re.search(address_pattern, text, re.IGNORECASE) is not None

        for row in shift_rows:
            try:
                class_list = row.get_attribute("class").split()
                date_key = extract_date(class_list)
                if not date_key:
                    continue
                time_text = row.find_element(By.CSS_SELECTOR, "td.second").text.strip().split("\n")[-1]
                school_and_address = row.find_element(By.CSS_SELECTOR, "td.fourth").text.strip()
                parts = school_and_address.split("\n")
                school_name = parts[0].strip() if len(parts) > 0 else "Unknown School"
                raw_address = parts[1].strip() if len(parts) > 1 else ""
                address = raw_address if is_valid_address(raw_address) else "Unknown Address"
                shift_data.append({"school": school_name, "date": date_key, "time": time_text, "address": address})
            except Exception as e:
                print(f"⚠️ Error reading row: {e}")

    except Exception as e:
        print(f"❌ Sync failed: {e}")
    finally:
        driver.quit()

    for shift in shift_data:
        full_name = shift["school"]
        date_key = shift["date"]
        time_val = shift["time"]
        address = shift["address"]

        sport = "General"
        base_name = full_name
        for sport_name in common_sports:
            if sport_name.lower() in full_name.lower():
                sport = sport_name.capitalize()
                base_name = full_name.lower().replace(sport_name.lower(), "").strip()
                break

        normalized_name = normalize_name(base_name)
        match = next((s for s in schools if normalize_name(s.name) == normalized_name), None)
        if not match:
            match = School(name=base_name.title(), address=address, phone_number="Unknown")
            schools.append(match)

        if sport not in match.sub_schools:
            match.add_sub_school(sport)
        match.sub_schools[sport].schedule[date_key] = time_val

    return schools