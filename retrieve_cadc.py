import requests
import argparse 
import json
import pandas as pd


def fetch_cadc(year):
    url = f"https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/meetings/meetings?year={year}"
    r = requests.get(url, timeout = 20)
    r.raise_for_status()
    conferences_list = r.json()
    return conferences_list

def clean_info(conferences_list, 
               extra_keys = None):
    save_keys = set(["title", "start", "end", "location", "web1", "keywords"])
    if extra_keys is not None:
        save_keys = save_keys + set(extra_keys)
    clean_conferences_list = []
    for conference in conferences_list:
        new_dict = {key : conference.get(key, None) for key in save_keys}
        clean_conferences_list.append(new_dict)
    return clean_conferences_list


parser = argparse.ArgumentParser(description="Retrieves meetings listed on " \
                                 "the Canadian Astronomy Data Centre website")
parser.add_argument("-y", "--year", action = "store", required = True, type=int)
parser.add_argument("-f", "--format", action = "store", choices=['json', 'csv'], default = "json")
parser.add_argument("--out", action = "store", type = str)
args = parser.parse_args()

output = args.out or str(args.year)
outname = f"{output}.{args.format}"

conferences_list = fetch_cadc(args.year)
if len(conferences_list) < 1:
    raise ValueError("Could not retrieve any meetings")
conferences_list = clean_info(conferences_list)

if args.format == "json":
    with open(outname, "w") as f:
        json.dump(conferences_list, f, indent = 4, ensure_ascii=False)
elif args.format == "csv":
    keys = conferences_list[0].keys()
    data = {key : [conference[key] for conference in conferences_list] for key in keys}
    df = pd.DataFrame(data).sort_values(by="start")
    df.to_csv(outname, index = False)


