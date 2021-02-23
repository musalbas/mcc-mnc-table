# Get the Mobile Country Codes (MCC) and Mobile Network Codes (MNC) table
# from mcc-mnc.com and output it in CSV format.

import re
import urllib.request

print("MCC,MCC (int),MNC,MNC (int),ISO,Country,Country Code,Network")

td_re = re.compile('<td>([^<]*)</td>'*6)

with urllib.request.urlopen('http://mcc-mnc.com/') as f:
    html = f.read().decode('utf-8')
    tbody_start = False
    for line in html.split('\n'):
        if '<tbody>' in line:
            tbody_start = True
        elif '</tbody>' in line:
            break
        elif tbody_start:
            td_search = td_re.search(line)
            csv_line = ''
            for n in range(1, 7):
                group = td_search.group(n).strip().replace(',', '')
                csv_line += group
                if n == 1:
                    csv_line += ',' + str(int(group, 16))
                elif n == 2:
                    if len(group) == 2:
                        mnc_int = int(group + 'f', 16)
                    elif group != 'n/a':
                        mnc_int = int(group, 16)
                    csv_line += ',' + str(mnc_int)
                if n != 6:
                    csv_line += ','
            print(csv_line)
