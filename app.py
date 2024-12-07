from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import csv

app = Flask(__name__)
socketio = SocketIO(app)
user_data = {}

# Selenium setup
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return uc.Chrome(options=options)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import csv

def scrape_portal(addresses, driver, output_filename):
    driver.get("https://sandiegoca.c3swift.com/")
    driver.find_element(By.ID, "email").send_keys("Spencer@cal-backflow.com")
    driver.find_element(By.ID, "password").send_keys("RWTSandiego90")
    driver.find_element(By.CLASS_NAME, "mainBtn").click()
    time.sleep(5)

    # Start a new test
    driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div[1]/a').click()

    with open(output_filename, 'w', newline='') as csvfile:
        fieldnames = ['Location Name', 'Location Address', 'Status', 'Serial Number', 'Assembly Type', 'Make', 'Model', 'Size']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for address in addresses:
            driver.find_element(By.NAME, "location_address").clear()
            driver.find_element(By.NAME, "location_address").send_keys(f"{address['ZIP Code']} {address['Location']}")
            driver.find_element(By.XPATH, '//*[@id="locationAssemblyInfo"]/div/div[4]/button').click()
            time.sleep(3)

            # Wait for the location table to be present
            location_table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "rt-tr-group"))
            )

            # Extract data from the location table
            location_rows = location_table.find_elements(By.CLASS_NAME, "rt-tr")
            for location_row in location_rows:
                location_name = location_row.find_element(By.CLASS_NAME, "rt-td").text
                location_address = location_row.find_elements(By.CLASS_NAME, "rt-td")[2].text

            # Wait for the assembly table to be present
            assembly_table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.rt-tr.-odd"))
            )

            # Extract data from the assembly table
            assembly_rows = assembly_table.find_elements(By.CSS_SELECTOR, "div.rt-tr.-odd")
            for assembly_row in assembly_rows:
                status = assembly_row.find_element(By.CSS_SELECTOR, "div.rt-td:nth-child(2)").text
                serial_number = assembly_row.find_element(By.CSS_SELECTOR, "div.rt-td:nth-child(3)").text
                assembly_type = assembly_row.find_element(By.CSS_SELECTOR, "div.rt-td:nth-child(4)").text
                make = assembly_row.find_element(By.CSS_SELECTOR, "div.rt-td:nth-child(5)").text
                model = assembly_row.find_element(By.CSS_SELECTOR, "div.rt-td:nth-child(6)").text
                size = assembly_row.find_element(By.CSS_SELECTOR, "div.rt-td:nth-child(7)").text

                writer.writerow({
                    'Location Name': location_name,
                    'Location Address': location_address,
                    'Status': status,
                    'Serial Number': serial_number,
                    'Assembly Type': assembly_type,
                    'Make': make,
                    'Model': model,
                    'Size': size
                })

    

# Scraping function for google maps
def scrape_google_maps(zip_code, session_id):
    driver = setup_driver()
    driver.get("https://www.google.com/maps")

    time.sleep(3)

    if driver.current_url != "https://www.google.com/maps":
        driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[1]/div/div/button/span').click()
    
    socketio.emit('log', {'data': f"Started scraping for ZIP Code: {zip_code}"}, to=session_id)

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(f"{zip_code}")
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    addresses = []
    scroll_count = 1
    
    for i in range(scroll_count):
        try:
            results = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc[aria-label]')
            for result in results:
                address = result.get_attribute("aria-label")
                if address:
                    zip_code_extracted = re.search(r'\b\d{5}\b', address).group()
                    location_name = address.replace(zip_code_extracted, "").strip(", ")
                    addresses.append({"Location": location_name, "ZIP Code": zip_code_extracted})
            socketio.emit('log', {'data': f"Scroll {i+1} completed, found {len(addresses)} addresses"}, to=session_id)
            driver.execute_script("document.querySelector('div[role=\"feed\"]').scrollBy(0, 1000);")
            time.sleep(3)
        except:
            break
    
    filename = f"addresses_{zip_code}.csv"
    scrape_portal(addresses, driver, filename)
    user_data[session_id] = filename
    socketio.emit('scrape_complete', {'filename': filename}, to=session_id)




# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result/<session_id>')
def result(session_id):
    return render_template('result.html', session_id=session_id)

@app.route('/scrape', methods=['POST'])
def scrape():
    zip_code = request.form.get('zip_code')
    session_id = request.form.get('session_id')
    threading.Thread(target=scrape_google_maps, args=(zip_code, session_id)).start()
    return redirect(url_for('status', session_id=session_id))

@app.route('/status/<session_id>')
def status(session_id):
    return render_template('status.html', session_id=session_id)

@app.route('/download/<session_id>')
def download_file(session_id):
    filename = user_data.get(session_id)
    if filename:
        return send_file(filename, as_attachment=True)
    return jsonify({"error": "File not found or scrape not complete"}), 404

@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'Connected to server'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
