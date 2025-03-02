from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import csv
import random
import time

# Tor SOCKS proxy settings
TOR_PROXY = "socks5h://127.0.0.1:9150"  # Default Tor Browser SOCKS proxy port

# List of user-agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.119 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.129 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
]

# Select a random User-Agent
random_user_agent = random.choice(USER_AGENTS)

# Set up Firefox options
options = Options()
options.set_preference("network.proxy.type", 1)
options.set_preference("network.proxy.socks", "127.0.0.1")
options.set_preference("network.proxy.socks_port", 9150)  # Tor default SOCKS port
options.set_preference("network.proxy.socks_remote_dns", True)  # Ensures .onion resolution
options.set_preference("places.history.enabled", False)  # Disable history tracking
options.set_preference("privacy.clearOnShutdown.cookies", True)  # Auto-clear cookies
options.set_preference("browser.privatebrowsing.autostart", True)  # Force private mode
options.set_preference("general.useragent.override", random_user_agent) # Set random User-Agent
options.set_preference("dom.webdriver.enabled", False)  # Hide WebDriver
options.set_preference("useAutomationExtension", False)  # Disable automation detection
options.set_preference("media.peerconnection.enabled", False)  # Disable WebRTC leaks
options.set_preference("network.http.referer.spoofSource", True)  # Spoof referer
options.set_preference("privacy.resistFingerprinting", True)  # Avoid fingerprint tracking

# Start Firefox with Tor proxy
driver = webdriver.Firefox(options=options)

# Wait for Tor to fully connect
time.sleep(10)  # Add a delay before making the request

# list of companies
companies_list = []

# list of companies details
companies_details = []

# ** This is to get the content of the page
def get_content_list(url):
    driver.get(url)
    # implement waiting for the page to load
    driver.implicitly_wait(30)
    # get content
    content = driver.page_source
    return content

# ** parse the content of the page
def parse_main_content(content):
    soup = BeautifulSoup(content, "html.parser")
    # Parse with BeautifulSoup
    cards = soup.find_all("a", class_="index-anchor")

    for card in cards:
        # Extract href (link)
        href = card["href"].strip()
        href = "http://ransomxifxwc5eteopdobynonjctkxxvap77yqifu2emfbecgbqdw6qd.onion/" + href

        # Extract company website
        company_name = card.find("div", class_="card-title").text.strip()

        # Extract visits and data size
        visits = card.find(text=lambda text: text and "Visits:" in text)
        data_size = card.find(text=lambda text: text and "Data Size:" in text)

        if visits and data_size:
            visits = visits.split(":")[1].strip()
            data_size = data_size.split(":")[1].strip()


        # Extract timestamp (last div in the card)
        timestamp = card.find("div", class_="card-footer").text.strip()

        # Append to companies_list
        companies_list.append({
            "link": href,
            "company_name": company_name,
            "visits": visits,
            "data_size": data_size,
            "timestamp": timestamp
        })

    return companies_list

# ** This is to extract the company details from the html content
def parse_company_details(content):
    soup = BeautifulSoup(content, "html.parser")

    # Find the element with class 'post-content'
    post_content = soup.find('div', class_='post-content')

    if post_content:
        post_content = post_content.get_text(strip=True)
    
    return post_content

# ** iterate over the companies list and get the details of each company and store it in the companies_details list
def get_company_details():
    for company in companies_list:
        # Get the content of the page
        content = get_content_list(company["link"])
        # Parse the content of the page
        company_details = parse_company_details(content)

        # Append to companies_details
        companies_details.append({
            "company_name": company["company_name"],
            "visits": company["visits"],
            "data_size": company["data_size"],
            "timestamp": company["timestamp"],
            "link": company["link"],
            "company_details": company_details
        })
    
    return companies_details

# ** This is to save the html file to the local directory (This is for testing purposes only)
def save_html_file(content):
    with open("RansomHubMain.html", "w", encoding="utf-8") as file:
        file.write(content)
        file.close()

# ** This is to load the html file from the local directory (This is for testing purposes only)
def load_local_file():
    with open("RansomHubMain.html", "r", encoding="utf-8") as file:
        content = file.read()
    return content

# ** save companies details to a CSV file
def save_companies_details_to_csv():
    with open("RansomHubData_V0.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["Company Name", "Visits", "Data Size", "Date", "Link", "Company Details"])
        # Write rows
        for company in companies_details:
            writer.writerow([
                company["company_name"],
                company["visits"],
                company["data_size"],
                company["timestamp"],
                company["link"],
                company["company_details"]
            ])

if __name__ == "__main__":
    URL = "http://ransomxifxwc5eteopdobynonjctkxxvap77yqifu2emfbecgbqdw6qd.onion/"
    content = get_content_list(URL)

    # save the output to a html file (for testing purposes only)
    # save_html_file(content)

    # load the content from the local file (for testing purposes only)
    # main_Page = load_local_file()

    # parse the content of the page 
    companies_list = parse_main_content(content)

    # print the companies list
    print("Number of Listed companies:" + str(len(companies_list)))

    # get the details of each company
    companies_details = get_company_details()

    # number of companies details saved
    print("Number companies details saved:" + str(len(companies_details)))

    # save the companies details to a csv file
    save_companies_details_to_csv()

    # quit the driver
    driver.quit()