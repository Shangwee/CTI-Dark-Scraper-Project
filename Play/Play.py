from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import csv
import random
import time
import re
import pickle

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

# # Wait for Tor to fully connect
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

# ** This is to get the max page number of the site
def get_page_number(content):
    soup = BeautifulSoup(content, "html.parser")
    # Find all spans with the class "Page"
    pages = soup.find_all('span', class_='Page')
    # Get the last page number
    last_page_number = pages[-1].text.strip()
    return last_page_number

# ** parse the content of the page
def parse_main_content(content):
    soup = BeautifulSoup(content, "html.parser")
    views_pattern = r"views:\s*(\d+)"
    added_date_pattern = r"added:\s*(\d{4}-\d{2}-\d{2})"
    pub_date_pattern = r"publication date:\s*(\d{4}-\d{2}-\d{2})"
    cards = soup.find_all("th", class_="News")
    for card in cards:
        match = re.search(added_date_pattern, card.text)
        # check if it is in the 2024 date range
        # if yes, extract details else continue / return
        if match:
            added_date = match.group(1)
            added_year = int(added_date.split('-')[0])
            print(f"Added year: {added_year}")
            # Compare the year to 2024
            if added_year < 2024:
                return None
            elif added_year > 2024:
                continue
        data = {}

        # Extract name
        data['company_name'] = card.contents[0].strip()
        all_divs = card.find_all('div')

        # Extract location
        location_i_tag = card.find('i', class_='location')
        if location_i_tag and location_i_tag.find_next_sibling(string=True):
            data['location'] = location_i_tag.find_next_sibling(string=True).strip()

        # Extract company link
        link_i_tag = card.find('i', class_='link')
        if link_i_tag and link_i_tag.find_next_sibling(string=True):
            data['company_link'] = link_i_tag.find_next_sibling(string=True).strip()

        # Extract href
        onclick_attr = card.get('onclick')
        if onclick_attr:
            match = re.search(r"viewtopic\('([^']+)'\)", onclick_attr)
            if match:
                data['href'] = "http://mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion/topic.php?id=" + match.group(1)
        
        for div in all_divs:
            div_text = div.get_text(strip=True)
            
            # Extract views
            views_match = re.search(views_pattern, div_text)
            if views_match:
                data['views'] = views_match.group(1)

            # Extract added date
            added_date_match = re.search(added_date_pattern, div_text)
            if added_date_match:
                data['added_date'] = added_date_match.group(1)
            
            # Extract publication date
            pub_date_match = re.search(pub_date_pattern, div_text)
            if pub_date_match:
                data['publication_date'] = pub_date_match.group(1)

        # Append to companies_list
        companies_list.append(data)

    return companies_list

# ** This is to extract the company details from the html content
def parse_company_details(content):
    soup = BeautifulSoup(content, "html.parser")
    company_data = {}
    # regex pattern to extract data size, company information, data information
    size_pattern = r"amount of data:\s*(.*gb)"
    information_pattern = r"information:\s*(.*?)(?=\n|comment:|$)"
    comment_pattern = r"comment:\s*(.*?)(?=\n|DOWNLOAD LINKS:|$)"
    all_divs = soup.find_all('div')
    for div in all_divs:
        div_text = div.get_text(strip=True)

        # Extract data_size
        size_match = re.search(size_pattern, div_text)
        if size_match:
            company_data['data_size'] = size_match.group(1).strip()

        # Extract company_info
        company_info_match = re.search(information_pattern, div_text)
        if company_info_match:
            company_data['company_details'] = company_info_match.group(1).strip()

        # Extract data_info
        data_info_match = re.search(comment_pattern, div_text)
        if data_info_match:
            company_data['data_info'] = data_info_match.group(1).strip()
            
    return company_data

# ** iterate over the companies list and get the details of each company and store it in the companies_details list
def get_company_details():
    for company in companies_list:
        # Get the content of the page
        content = get_content_list(company["href"])
        # Parse the content of the page
        company_details = parse_company_details(content)
        # merge company information from parse_main_content() and parse_company_details()
        merged_company_details = {**company, **company_details}
        # Append to companies_details
        companies_details.append(merged_company_details)
    
    return companies_details

# ** This is to save the html file to the local directory (This is for testing purposes only)
def save_html_file(content):
    with open("Play.html", "w", encoding="utf-8") as file:
        file.write(content)
        file.close()

# ** This is to load the html file from the local directory (This is for testing purposes only)
def load_local_file():
    with open("Play.html", "r", encoding="utf-8") as file:
        content = file.read()
    return content

# ** save companies details to a CSV file
def save_companies_details_to_csv():
    with open("PlayData_V0.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["Company Name", "Company Link", "Company Details", "Location", "Visits", "Added Date", "Publication Date", "Ransomware Link", "Data Size", "Data Information"])
        # Write rows
        for company in companies_details:
            writer.writerow([
                company["company_name"],
                company["company_link"],
                company["company_details"],
                company["location"],
                company["views"],
                company["added_date"],
                company["publication_date"],
                company["href"],
                company["data_size"],
                company["data_info"]

            ])

if __name__ == "__main__":
    URL = "http://mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion"
    content = get_content_list(URL)
    page_number = int(get_page_number(content))
    # go through each page and get content
    # start from 5 because 5 is the first page with 2024 posts, adjust accordingly
    for i in range(5, page_number + 1):
        content = get_content_list(f"http://mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion/index.php?page={str(i)}")
        check = parse_main_content(content)
        # check returns none when date < 2024 // stop when date out of range
        if check is None:
            break
    print(companies_list)

    # save the output to a html file (for testing purposes only)
    # save_html_file(content)

    # load the content from the local file (for testing purposes only)
    # content = load_local_file()

    # # print the companies list
    print("Number of Listed companies:" + str(len(companies_list)))

    # save company list into a pickle file for easy access
    with open("companies_list.pkl", "wb") as file:
        pickle.dump(companies_list, file)

    # # get the details of each company
    companies_details = get_company_details()

    # save company details into a pickle file for easy access
    with open("companies_details.pkl", "wb") as file:
        pickle.dump(companies_details, file)

    # # number of companies details saved
    print("Number companies details saved:" + str(len(companies_details)))

    # # save the companies details to a csv file
    save_companies_details_to_csv()

    # quit the driver
    driver.quit()