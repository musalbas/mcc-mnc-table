# Get the Mobile Country Codes (MCC) and Mobile Network Codes (MNC) table
# from mcc-mnc.com and output it in XML format.

import re
import urllib2
import xml.etree.ElementTree as element_tree
import xml.dom.minidom as minidom

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

root_element = element_tree.Element('carriers')

for carrier in mcc_mnc_list:
    sub_element = element_tree.Element('carrier')

    for key, value in carrier.items():
        child_element = element_tree.Element(key)
        child_element.text = value
        sub_element.append(child_element)

    root_element.append(sub_element)

print minidom.parseString(element_tree.tostring(root_element)).toprettyxml(indent = '    ')
