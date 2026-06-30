import requests
from bs4 import BeautifulSoup
from datetime import datetime

_KEYWORD_DICTIONARY = {
    "Meeting Location" : "Location",
    "Meeting Dates" : "Dates",
    "Abstract Deadline" : "abstract_deadline",
    "Early Registration Deadline" : "early_registration_deadline",
    "Late Registration Deadline" : "late_registration_deadline",
    "Registration Deadline" : "registration_deadline",
}

url = "https://heasarc.gsfc.nasa.gov/docs/heasarc/meetings.html"


def get_info_dictionary(conference_description):
    info_dictionary = {}
    keywords = conference_description.find_all("dd")
    for keyword in keywords:
        lines = keyword.get_text(separator = "\n").splitlines()
        lines= [l.strip() for l in lines]

        for line in lines:
            for key, new_key in _KEYWORD_DICTIONARY.items():
                text_to_find = key + ":"
                if line.startswith(text_to_find):
                    info_dictionary[new_key] = line.split(":", 1)[1].strip()
    return info_dictionary

def get_title_link(conference_title_and_link):
    link = conference_title_and_link.find("a")["href"].strip()
    title = conference_title_and_link.get_text(strip=True).split(":")[0].strip()
    return title, link


def parse_date(date, range = False):
    if range:
        left, right  = date.split("-")
        left = left.strip()
        right = right.strip()
        start_date = datetime.strptime(left, "%Y %b %d").date()
        if len(right.split(" ")) > 1:
            #has month
            right = str(start_date.year) + " " + right
            end_date = datetime.strptime(right, "%Y %b %d").date()
        else:
            #right is only the day
            end_date = datetime(start_date.year, start_date.month, int(right)).date()
        return start_date, end_date
    
    parsed_date  = datetime.strptime(date.strip(), "%Y %b %d").date()
    return parsed_date



r = requests.get(url)
r.raise_for_status()
soup = BeautifulSoup(r.content, 'html.parser')


conferences_titles_and_links = soup.find_all("h4", class_ = "usa-accordion__heading")
conferences_descriptions = soup.find_all("div", class_ = "usa-accordion__content usa-prose")

if not len(conferences_descriptions) ==len(conferences_titles_and_links):
    raise ValueError("scraped Titles and descriptions have different lengths")

all_results = []
for idx in range(len(conferences_descriptions)):
    results = get_info_dictionary(conferences_descriptions[idx])
    results["title"], results["website"] = get_title_link(conferences_titles_and_links[idx])
    results["start"], results["end"] = parse_date(results["Dates"], range = True)
    results["start"] = str(results["start"])
    results["end"] = str(results["end"])
    for key in results.keys():
        if "_deadline" in key:
            results[key] = str(parse_date(results[key]))
    all_results.append(results)

###need to do something with the results