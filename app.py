from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO
import threading
import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Flask setup
app = Flask(__name__)
socketio = SocketIO(app)

# Store user-scraped data
user_data = {}

# Selenium WebDriver setup
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Anti-detection measure
    return uc.Chrome(options=options)

# Background scraping function
def scrape_google_maps(zip_code, session_id):
    driver = setup_driver()
    driver.get("https://www.google.com/maps")
    
    # Search for addresses within the zip code
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(f"{zip_code}")  # Include state for better results
    search_box.send_keys(Keys.RETURN)
    
    time.sleep(5)  # Allow time for results to load
    
    addresses = set()  # Use a set to avoid duplicates
    scroll_count = 10  # Number of scrolls to attempt
    
    for _ in range(scroll_count):
        try:
            # Locate address elements (adjust selector to target links with addresses)
            results = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc[aria-label]')
            print(results)
            if results == []:
                raise Exception("No results found")
        
            for result in results:
                address = result.get_attribute("aria-label")
                if address:
                    addresses.add(address)
            
            print("Finished first Try")
            # Scroll down to load more results
            try:
                driver.execute_script("document.querySelector('div[role=\"feed\"]').scrollBy(0, 1000);")
                print("Finished Last Try")
            except:
                print("Error scrolling")
                break
            time.sleep(3)  # Adjust based on page load time
        except:
            print("Error finding results from a element")
            results = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[1]/h1').text
            print(results)
            addresses.add(results)
            break

    print(addresses)
    driver.quit()
    
    # Save results in a CSV file and store them for download
    df = pd.DataFrame(list(addresses), columns=["Address"])
    filename = f"addresses_{zip_code}.csv"
    df.to_csv(filename, index=False)
    
    user_data[session_id] = filename
    socketio.emit('scrape_complete', {'session_id': session_id, 'filename': filename})

# Route to start the scraping process
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    zip_code = data.get('zip_code')
    session_id = data.get('session_id')
    
    # Start background scraping thread
    threading.Thread(target=scrape_google_maps, args=(zip_code, session_id)).start()
    
    return jsonify({"message": "Scraping started", "session_id": session_id}), 202

# Route to download the scraped data
@app.route('/download/<session_id>', methods=['GET'])
def download_file(session_id):
    if session_id in user_data:
        filename = user_data[session_id]
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({"error": "File not found or scrape not complete"}), 404

# Socket.IO route to check scrape status
@socketio.on('connect')
def handle_connect():
    print('Client connected')

# Run the Flask app
if __name__ == '__main__':
    socketio.run(app, debug=True)
