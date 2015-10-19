# Get the Mobile Country Codes (MCC) and Mobile Network Codes (MNC) table
# from mcc-mnc.com and output it in JSON format.

import re
import urllib2
import json

td_re = re.compile('<td>([^<]*)</td>'*6)

html = urllib2.urlopen('http://mcc-mnc.com/').read()

tbody_start = False

mcc_mnc_list = []

for line in html.split('\n'):
    if '<tbody>' in line:
        tbody_start = True
    elif '</tbody>' in line:
        break
    elif tbody_start:
        td_search = td_re.search(line)
        current_item = {}
        td_search = td_re.split(line)

        current_item['mcc'] = td_search[1]
        current_item['mnc'] = td_search[2]
        current_item['iso'] = td_search[3]
        current_item['country'] = td_search[4]
        current_item['country_code'] = td_search[5]
        current_item['network'] = td_search[6][0:-1]

        mcc_mnc_list.append(current_item)

print json.dumps(mcc_mnc_list, indent=2)
