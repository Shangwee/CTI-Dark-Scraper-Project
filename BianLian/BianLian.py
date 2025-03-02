from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import csv
import random

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

# list of companies
companies_list = []

# list of companies details
companies_details = []

# ** This is to get the content of the page
def get_content_list(url):
    driver.get(url)
    # implement waiting for the page to load
    driver.implicitly_wait(15)
    # get content
    content = driver.page_source
    return content

# ** This is to load the html file from the local directory (This is for testing purposes only)
def load_local_file():
    with open('BianLianCompanyList.html', 'r', encoding='utf-8') as file:
        content = file.read()
    return content

# ** This is to extract the company list from the html content between the date of 2024 and 2025
def parse_companies_list_content(content):
    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract all list items inside the <ul class="posts">
    companies = soup.find_all("li", class_="post")

    for company in companies:
        # Extract company name
        company_name = company.find("a").text.strip()

        # Extract company link (href)
        company_href = company.find("a")["href"].strip()

        # Extract date
        date = company.find("span", class_="meta").text.strip()

        # Extract year from the date (assumes format: "Month Day, Year")
        year = int(date.split()[-1])  # Last part of the date string is the year

        # full link
        company_href = baseURL + company_href

        # Filter: Only keep entries from 2024 and later
        if year >= 2024:
            # Store in list
            companies_list.append({"name": company_name, "href": company_href, "date": date})

    return companies_list

# ** This is to extract the company details from the html content
def parse_company_details(content):
    soup = BeautifulSoup(content, 'html.parser')

    ### **Extract Data Descriptions**
    data_description_section = soup.find("section", class_="body")  # Locate section with data
    data_descriptions = [li.text.strip() for li in data_description_section.find_all("li")]

    ### **Extract Tags**
    tag_section = soup.find("ul", class_="tags")  # Locate the tag container
    tags = [tag.text.strip() for tag in tag_section.find_all("a")]

    ### **Extract Data Volume**
    # Find the paragraph containing "Data volume"
    data_volume = "N/A"
    for p in soup.find_all("p"):
        if "Data volume" in p.text:
            data_volume = p.text.split(":")[1].strip()
            break  # Stop after finding the first match

    # Print extracted results
    print("Data Descriptions:")
    for desc in data_descriptions:
        print(f"- {desc}")

    print("\nTags:")
    for tag in tags:
        print(f"- {tag}")

    print(f"\nData Volume: {data_volume}")

    return data_descriptions, tags, data_volume

# ** iterate over the companies list and get the details of each company and store it in the companies_details list
def get_companies_details():
    for company in companies_list:
        # Get the content of the page
        content = get_content_list(company["href"])
        # Parse the content
        data_descriptions, tags, data_volume = parse_company_details(content)
        # Store the details
        companies_details.append({"name": company["name"], "data_descriptions": data_descriptions, "tags": tags, "date": company["date"], "href": company["href"], "data_volume": data_volume})

    return companies_details

# ** save companies details to a CSV file
def save_companies_details_to_csv():
    with open('BianLianData_V0.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "Data Descriptions", "Tags", "Date", "Link", "Data Volume"])
        for company in companies_details:
            writer.writerow([company["name"], ", ".join(company["data_descriptions"]), ", ".join(company["tags"]),",".join(company["date"]), ", ".join(company["href"]), ", ".join(company["data_volume"])])

# Main function
if __name__ == "__main__":
    # Visit an .onion site
    url = "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/companies/"
    baseURL = "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion"

    # Get the content of the page
    html_content = get_content_list(url)

    companies_list = parse_companies_list_content(html_content)

    # Print the list of companies
    print("List of Companies:" + str(len(companies_list)))

    # Get the details of each company
    companies_details = get_companies_details()

    # Print the details of each company
    print("Details of Companies:" + str(len(companies_details)))

    # Save the details to a CSV file
    save_companies_details_to_csv()

    # Close the browser
    driver.quit()



