"""Train tickets query from CLI.

Usage:
  tickets.py [-dgzkt] <date> <from> <to>

Options:
  -h --help        Show this screen.
  -v --version     Show version.
  -d               动车
  -g               高铁
  -z               直达
  -k               快车
  -t               特快

"""
from docopt import docopt
import stations
import requests
import warnings
import re
import datetime
from prettytable import PrettyTable
from colorama import Fore


class CLI(object):
    def __init__(self):
        self.arguments = docopt(__doc__, version='Train Ticket query 1.0')
        self.train_date = self.arguments['<date>']
        self.from_station = self.arguments['<from>']
        self.to_station = self.arguments['<to>']
        self.options = ''.join([key.strip('-') for key, values in self.arguments.items() if values is True])
        self.base_url = ('https://kyfw.12306.cn/otn/leftTicket/queryX?leftTicketDTO.'
                         'train_date={}&'
                         'leftTicketDTO.from_station={}&'
                         'leftTicketDTO.to_station={}&'
                         'purpose_codes=ADULT')

    def check_arguments_validity(self):
        if not re.findall(r'(\d{4})\D?(\d{2})\D?(\d{2})', self.train_date):
            # 为了最大限度的匹配日期格式
            exit('日期格式不正确')
        else:
            self.train_date = '-'.join(re.findall(r'(\d{4})\D?(\d{2})\D?(\d{2})', self.train_date)[0])
            if datetime.datetime.strptime(self.train_date, '%Y-%m-%d') < datetime.datetime.now():
                exit('请输入有效的日期')
        if self.from_station is None or self.to_station is None:
            exit('出发站或终点站不得为空')
        else:
            if stations.get_station_code(self.from_station) is None or stations.get_station_code(self.to_station) is None:
                exit('请输入有效的车站信息')
            else:
                self.from_station = stations.get_station_code(self.from_station)
                self.to_station = stations.get_station_code(self.to_station)
        return True

    @staticmethod
    def color(color, string):
        return getattr(Fore, color.upper()) + string + Fore.RESET

    def request(self):
        if self.check_arguments_validity():
            # print(self.base_url.format(self.train_date, self.from_station, self.to_station))
            r = requests.get(self.base_url.format(self.train_date, self.from_station, self.to_station), verify=False)
            # r = requests.get(URL_Template.format('2017-10-01', 'GZQ', 'CBQ'), verify=False)
            # print(r.status_code)
            if r.status_code == 200:
                try:
                    trains = r.json()["data"]["result"]
                except Exception as e:
                    exit('请求出错，请重试')
                else:
                    x = PrettyTable()
                    x.field_names = ["车次", "车站", "时间", "历时", "商务", "一等座", "二等座", "无座", "软卧", "硬卧"]
                    for train in trains:
                        train_info = train.strip().split('|')
                        train_no = train_info[3]
                        if self.options and train_no[0].lower() not in self.options:
                            continue
                        from_station_name = stations.get_station_name(train_info[6])
                        to_station_name = stations.get_station_name(train_info[7])
                        start_time = train_info[8]  # 出发时间
                        arrive_time = train_info[9]  # 到达时间
                        during_time = train_info[10]  # 历时
                        business_seat = train_info[32] or '--'  # 商务座
                        # principal_seat = train_info[25] or '--'   # 特等座
                        first_class_seat = train_info[31] or '--'  # 一等座
                        second_class_seat = train_info[30] or '--'  # 二等座
                        without_seat = train_info[26] or '--'  # 无座
                        soft_sleeper = train_info[23] or '--'  # 软卧
                        hard_sleeper = train_info[28] or '--'  # 硬卧
                        x.add_row([train_no,
                                   '\n'.join([from_station_name, to_station_name]),
                                   '\n'.join([start_time, arrive_time]),
                                   during_time,
                                   business_seat,
                                   first_class_seat,
                                   second_class_seat,
                                   without_seat,
                                   soft_sleeper,
                                   hard_sleeper])
                    print(x)


if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    # URL_Template = ('https://kyfw.12306.cn/otn/leftTicket/queryX?leftTicketDTO.'
    #                 'train_date={}&'
    #                 'leftTicketDTO.from_station={}&'
    #                 'leftTicketDTO.to_station={}&'
    #                 'purpose_codes=ADULT')
    cli = CLI()
    cli.request()

    # arguments = docopt(__doc__, version='Train Ticket query 1.0')
    # print(arguments)

    # response = requests.get(URL_Template.format('2017-10-01', 'GZQ', 'CBQ'), verify=False)
    # print(response.status_code)
    # if response.status_code == 200:
    #     try:
    #         trains = response.json()['data']['result']
    #     except Exception as e:
    #         print(e)
    #         exit('请求出错，请重试')
    #     else:
    #         x = PrettyTable()
    #         x.field_names = ["车次", "车站", "时间", "历时", "商务座", "一等座", "二等座", "无座", "软卧", "硬卧"]
    #         for train in trains:
    #             train_info = train.strip().split('|')
    #             train_no = train_info[3]
    #             from_station_name = stations.get_station_name(train_info[6])
    #             to_station_name = stations.get_station_name(train_info[7])
    #             start_time = train_info[8]                  # 出发时间
    #             arrive_time = train_info[9]                 # 到达时间
    #             during_time = train_info[10]                # 历时
    #             business_seat = train_info[32] or '--'      # 商务座
    #             # principal_seat = train_info[25] or '--'   # 特等座
    #             first_class_seat = train_info[31] or '--'   # 一等座
    #             second_class_seat = train_info[30] or '--'  # 二等座
    #             without_seat = train_info[26] or '--'       # 无座
    #             soft_sleeper = train_info[23] or '--'       # 软卧
    #             hard_sleeper = train_info[28] or '--'       # 硬卧
    #             x.add_row([train_no,
    #                        '\n'.join([from_station_name, to_station_name]),
    #                        '\n'.join([start_time, arrive_time]),
    #                        during_time,
    #                        business_seat,
    #                        first_class_seat,
    #                        second_class_seat,
    #                        without_seat,
    #                        soft_sleeper,
    #                        hard_sleeper])
    #         print(x)
    #
    # # print('-'.join(re.findall(r'(\d{4})\D?(\d{2})\D?(\d{2})', '2010.01 0178')[0]))
    #
    # # print(stations.get_station_code('北京'))
