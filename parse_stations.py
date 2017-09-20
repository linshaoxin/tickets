import re
import requests
import warnings
import json


def parse_stations():
    r = requests.get('https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9026', verify=False)
    pattern = u'([\u4e00-\u9fa5]+)\|([A-Z]+)'
    groups = re.findall(pattern, r.text)
    names = list(map(lambda group: group[0], groups))
    codes = list(map(lambda group: group[1], groups))
    with open('stations.py', 'w', encoding='utf-8') as f:
        f.write('names = ')
        json.dump(names, f, ensure_ascii=False)
        f.write('\ncodes = ')
        json.dump(codes, f, ensure_ascii=False)

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    parse_stations()
