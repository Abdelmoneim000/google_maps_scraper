# ZIP Code Scraper Web App

A web application that allows users to scrape location data based on a provided ZIP code using Selenium and Google Maps.

## Features

- Accepts a ZIP code and session ID from the user.
- Scrapes location data from Google Maps based on the provided ZIP code.
- Displays real-time scraping progress using WebSockets (SocketIO).
- Provides a downloadable CSV file of the scraped data once the scraping is complete.
- Displays scraping status in a dedicated status page.

## Tech Stack

- **Backend**: Python, Flask, Flask-SocketIO
- **Web Scraping**: Selenium (with undetected_chromedriver for bypassing detection)
- **Frontend**: HTML, CSS, JavaScript
- **Real-time Communication**: WebSocket (via SocketIO)

## Installation

### Prerequisites

- Python 3.x installed
- Internet connection to download the necessary Python packages

### Windows Setup

1. Download and install Python from the [official website](https://www.python.org/downloads/).
2. Download the `requirements_windows.bat` file and double-click it to execute.
3. This will install all the necessary Python packages and launch the app in your default browser.

### Linux Setup

1. Ensure Python 3.x is installed. You can check by running:

   ```bash
   python3 --version
   ```
2. Download the requirements_linux.sh script and run it:
    ```bash
    bash requirements_linux.sh
    ```
    The script will install all the necessary Python packages and then run the app.


## Running the App
To run the app, simply execute the following command in the root directory of the project:

```bash
python app.py
```

The app will start running on http://127.0.0.1:5000. After running the app, it will automatically open the default browser at this address.


## Using the App
1. Visit http://127.0.0.1:5000.
2. Enter a ZIP code and a session ID.
3. Click "Start Scraping" to begin the process.
4. A status page will show the progress in real-time.
5. Once the scraping is complete, you will be redirected to the result page, where you can download the CSV file with the scraped data.


## Routes

- / - Home page where users can input the ZIP code and session ID.
- /scrape - Handles the form submission and starts the scraping process.
- /status/<session_id> - Displays real-time progress during scraping.
- /download/<session_id> - Allows users to download the CSV - file after scraping is complete.


## Dependencies

- Flask
- Flask-SocketIO
- Selenium
- undetected-chromedriver
- pandas

## License

This project is licensed under the MIT License - see the LICENSE file for details.

