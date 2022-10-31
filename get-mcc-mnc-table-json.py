import re
import json
import requests
from typing import List

DOMAIN: str = "https://mcc-mnc-list.com"
MAIN_JS_FILE: str = "main.0744a96a58a20d0b.js"
JSON_PATTERN: re.Pattern = re.compile(r"JSON.parse\('(\[.*\])'\),")  # very specific pattern, don't use it elsewhere XD


def create_json_file(url: str = f'{DOMAIN}/{MAIN_JS_FILE}', filename: str = "mcc-mnc-table.json") -> None:
    with open(filename, 'w', encoding='utf8') as f:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # returns an HTTPError object if an error has occurred during the process.
            json_string = JSON_PATTERN.findall(r.text)[0]  # finds only 1
            json_string = clean_json(json_string)
            f.write(prettify_json(json_string))


def prettify_json(json_data: str) -> str:
    json_object = json.loads(json_data)
    return json.dumps(json_object, indent=2, ensure_ascii=False)


def clean_json(json_data: str) -> str:
    """removing problematic unicode/combinations from received json string"""
    # removing garbage
    json_data = re.sub(r'"\\\\(?!")', '', json_data)
    json_data = re.sub(r'\\\\"', '', json_data)
    json_data = re.sub(r"\\\\n", '`', json_data)
    json_data = re.sub(r"\\'", '`', json_data)
    # fix un-decoded unicode objects
    for unicode in get_list_of_unicode(json_data):
        json_data = re.sub(rf'\{unicode}', eval(f"str('{unicode}')"), json_data)
    return json_data


def get_list_of_unicode(json_data: str) -> List[str]:
    """return lists of problematic unicode symbols existing in received json string"""
    unicode_set = set(re.findall(r"(\\x.{2,}?)", json_data))
    return list(unicode_set)


if __name__ == '__main__':
    create_json_file()

