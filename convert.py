import json, sys
import xml.etree.ElementTree as ET

"""
'last_unix_check' will automatically update based on the most recent ['dateVerified'] value
"""

def last_unix_check(set_unix=False, date_verified=None):
    unix_check_file = "data/last_unix_check"

    if set_unix and date_verified:
        with open(unix_check_file, "w") as u:
            u.write(str(date_verified))
    else:
        with open(unix_check_file, "r") as u:
            return str(u.read())

def analyze_json_data(json_file):
    with open(json_file, "r") as file:
        return json.load(file)
    
# Format incoming JSON time
def get_accurate_time(incoming_time) -> str:
    # The JSON export is in seconds
    incoming_time = float(incoming_time)

    # Check if the incoming time is over an hour
    hours = incoming_time // 3600
    seconds = incoming_time % 3600
    minutes = seconds // 60
    remaining_time = seconds % 60

    if hours > 0:
        return f"{int(hours)}:{int(minutes):02d}:{remaining_time:05.2f}"
    else:
        return f"{int(minutes)}:{remaining_time:05.2f}"
    
def convert_json_to_rss(json_file, rss_file):
    incoming_json_data = analyze_json_data(json_file)

    # RSS root
    rss_feed = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss_feed, "channel")

    # Global RSS items
    ET.SubElement(channel, "title").text = "Speedrun RSS Feed"
    ET.SubElement(channel, "link").text = f"https://www.speedrun.com/users/{incoming_json_data['user']['name']}"
    ET.SubElement(channel, "description").text = "Created by Sagemancer (https://github.com/sagemancer)"

    verified_dates = set()
    rss_update = False

    # Build RSS feed from JSON data
    for run in incoming_json_data.get("runList", []):
        date_verified = int(run['dateVerified'])
        verified_dates.add(date_verified)

        if date_verified > int(last_unix_check()):
            parent_element = ET.SubElement(channel, "runs")
            ET.SubElement(parent_element, "video").text = run['video']
            ET.SubElement(parent_element, "time").text = get_accurate_time(run['time'])
            rss_update = True
        else:
            pass

    rss_string = ET.tostring(rss_feed, encoding="utf-8", method="xml")

    # Export RSS feed
    if rss_update:
        with open(rss_file, "wb") as file:
            file.write(rss_string)

        last_unix_check(True, max(verified_dates))
        print(f"RSS feed successfully written to '{rss_file}'")
    else:
        print("RSS feed up to date")


if __name__ == "__main__":
    json_file = "data/src_user_export.json"
    rss_file = "api/output.rss"
    convert_json_to_rss(json_file, rss_file)
