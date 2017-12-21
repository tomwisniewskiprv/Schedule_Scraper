# -*- coding: utf-8 -*-
"""
    schedule_scraper_Deprecated.py

    Script scrapes web page content for schedule.

    Python 3.6

    10.06.2017 Tomasz Wisniewski


    Deprecated !!!!!
    This version is no longer supported.
"""
import time
import requests
from bs4 import BeautifulSoup


class ScheduleScraper(object):
    def __init__(self, url, group):
        # Scraped data storage
        self.time_table = self.create_time_table()
        self.friday = []
        self.saturday = []
        self.sunday = []

        self.url = url
        self.group = group

    def calculate_top_cord_for_hour(self, h, top_cord, top_jump):
        """
        Calculates coordinates from scraped data.

        :param h: full hour
        :param top_cord: initial value for top variable (scraped from website)
        :param top_jump: height difference between nodes
        :return: list with tuples (coordinates, time)
        """
        tab = []
        time_str = ''
        time_cod = 0

        for i in range(4):
            if i % 4 == 0:
                time_str = '{:0>2}:{:0<2}'.format((str(h)), str(i * 15))
                time_cod = top_cord
            if i % 4 == 1:
                time_str = '{:0>2}:{:0<2}'.format((str(h)), str(i * 15))
                time_cod = top_cord + top_jump
            if i % 4 == 2:
                time_str = '{:0>2}:{:0<2}'.format((str(h)), str(i * 15))
                time_cod = top_cord + 2 * top_jump
            if i % 4 == 3:
                time_str = '{:0>2}:{:0<2}'.format((str(h)), str(i * 15))
                time_cod = top_cord + 3 * top_jump

            tab.append([time_cod, time_str])

        next_hour_cords = top_cord + 4 * top_jump + 1
        return tab, next_hour_cords

    def create_time_table(self):
        """
        Creates time table as dictionary.
        :return: dictionary with time intervals (15 min)
        """
        time_table = {}
        hour = 8  # 8:00
        hour_last = 22  # last hour 21:00
        top_next_hour = 282  # initial value for 8:00
        top_jump = 11  # height difference between nodes

        for i in range(hour, hour_last):
            tmp_tab, top_next_hour = self.calculate_top_cord_for_hour(i, top_next_hour, top_jump)
            d = dict(tmp_tab)
            time_table.update(d)

        return time_table

    def main(self):
        """
        This for loop below is specially tailored to handle ugly source code from website.
        Aka Main Loop ()
        """
        # Actual scraping
        data = requests.get(self.url)
        soup = BeautifulSoup(data.content, 'html.parser')
        parsed = soup.prettify()

        tags_id = soup.find_all('div', class_='coursediv')

        for id in tags_id:
            if id.get_text().rstrip('\n') and id.get('style'):
                tags_id_a = id.find_all('a')
                subject = id.contents[1]
                tutor = tags_id_a[0].string.split()
                if len(tags_id_a) > 1:
                    room = tags_id_a[1].string
                else:
                    room = 'nieznany'

                end_reading = id.get('style').find('border')
                block_data = id.get('style')[:end_reading].replace('\n', '').split(';')
                block_data = [data.strip() for data in block_data]
                block_data = block_data[:len(block_data) - 1]

                coordinates = {}
                for data in block_data:
                    tmp_data = data.replace(' ', '').replace('px', '').split(':')
                    coordinates[tmp_data[0]] = int(tmp_data[1])

                print(coordinates)

                """
                MEMO :
                Source code from website has bugs. Some entries are doubled or tripled. I had decided to deal with
                redundant data in function remove_redundancy which will work on data sorted by group.
                
                I'm aware of this problem.
                """

                if coordinates['left'] == grpA1_friday:
                    if coordinates['width'] == one__grp:
                        self.friday.append(['A1', subject, tutor, room, coordinates])
                    elif coordinates['width'] == four_grp:
                        self.friday.append(['A1', subject, tutor, room, coordinates])
                        self.friday.append(['A2', subject, tutor, room, coordinates])
                        self.friday.append(['B3', subject, tutor, room, coordinates])
                        self.friday.append(['B4', subject, tutor, room, coordinates])
                if coordinates['left'] == grpA2_friday:
                    self.friday.append(['A2', subject, tutor, room, coordinates])
                if coordinates['left'] == grpB3_friday:
                    self.friday.append(['B3', subject, tutor, room, coordinates])
                if coordinates['left'] == grpB4_friday:
                    self.friday.append(['B4', subject, tutor, room, coordinates])

                if coordinates['left'] == grpA1_saturday:
                    if coordinates['width'] == one__grp:
                        self.saturday.append(['A1', subject, tutor, room, coordinates])
                    elif coordinates['width'] == four_grp:
                        self.saturday.append(['A1', subject, tutor, room, coordinates])
                        self.saturday.append(['A2', subject, tutor, room, coordinates])
                        self.saturday.append(['B3', subject, tutor, room, coordinates])
                        self.saturday.append(['B4', subject, tutor, room, coordinates])
                if coordinates['left'] == grpA2_saturday:
                    self.saturday.append(['A2', subject, tutor, room, coordinates])
                if coordinates['left'] == grpB3_saturday:
                    self.saturday.append(['B3', subject, tutor, room, coordinates])
                if coordinates['left'] == grpB4_saturday:
                    self.saturday.append(['B4', subject, tutor, room, coordinates])

                if coordinates['left'] == grpA1_sunday:
                    if coordinates['width'] == one__grp:
                        self.sunday.append(['A1', subject, tutor, room, coordinates])
                    elif coordinates['width'] == four_grp:
                        self.sunday.append(['A1', subject, tutor, room, coordinates])
                        self.sunday.append(['A2', subject, tutor, room, coordinates])
                        self.sunday.append(['B3', subject, tutor, room, coordinates])
                        self.sunday.append(['B4', subject, tutor, room, coordinates])
                if coordinates['left'] == grpA2_sunday:
                    self.sunday.append(['A2', subject, tutor, room, coordinates])
                if coordinates['left'] == grpB3_sunday:
                    self.sunday.append(['B3', subject, tutor, room, coordinates])
                if coordinates['left'] == grpB4_sunday:
                    self.sunday.append(['B4', subject, tutor, room, coordinates])  # legend

    def sort_data(self, data):
        """
        Sorts data by 'top' value which represents time!
        :param data: list
        :return: sorted list
        """
        result = []
        tmp_dict = {}

        for i in range(len(data)):
            tmp_dict[i] = data[i][4]['top']

        tmp_list_sorted = sorted(zip(tmp_dict.values(), tmp_dict.keys()))

        for i in tmp_list_sorted:
            result.append(data[i[1]])

        return result

    def sort_day_by_grp(self, data, grp):
        """
        Filters sorted list by group.
        :param data: sorted list
        :param grp: which group, must be a string
        :return: filtered list
        """
        result = []
        for d in data:
            if d[0] == grp:
                result.append(d)

        return result

    def remove_redundancy(self, data):
        """
        Clean results from redundant records.
        * function preserves order *

        :param data: sorted by grp list
        :return: cleaned sorted list
        """
        cleaned = []

        for record in data:
            if record not in cleaned:
                cleaned.append(record)

        return cleaned

    def display_results(self):

        # Sort out results
        self.friday_sorted = self.sort_data(self.friday)
        self.saturday_sorted = self.sort_data(self.saturday)
        self.sunday_sorted = self.sort_data(self.sunday)

        self.friday_sorted_by_grp = self.remove_redundancy(self.sort_day_by_grp(self.friday, self.group))

        self.saturday_sorted_by_grp = self.remove_redundancy(self.sort_day_by_grp(self.saturday_sorted, self.group))

        self.sunday_sorted_by_grp = self.remove_redundancy(self.sort_day_by_grp(self.sunday_sorted, self.group))

        print('FRIDAY:')
        for lesson in self.friday_sorted_by_grp:
            print(self.time_table[lesson[4]['top']], lesson[0], lesson[1], teachers.get(lesson[2][0], ''))

        print('SATURDAY:')
        for lesson in self.saturday_sorted_by_grp:
            print(self.time_table[lesson[4]['top']], lesson[0], lesson[1], teachers.get(lesson[2][0]))

        print('SUNDAY:')
        for lesson in self.sunday_sorted_by_grp:
            print(self.time_table[lesson[4]['top']], lesson[0], lesson[1], teachers.get(lesson[2][0]))

    def execute(self):
        t0 = time.clock()

        self.main()
        self.display_results()

        t1 = time.clock()
        print('time of execution:', t1 - t0)


teachers = {'MCh': 'Marcin Cholewa',
            'ASa': 'Arkadiusz Sacewicz',
            'PP': 'Piotr Paszek',
            'PG': 'Paweł Gładki',
            'MB': 'Barbara M. Paszek',
            'MaPa': 'Małgorzata Pałys',
            'LA': 'Aleksander Lamża',
            'TK': 'Katarzyna Trynda',
            'KP': 'Przemysław Kudłacik',
            'EK-W': 'Ewa Karolczak-Wawrzała',

            }

# All variables needed for correct data interpretation
# height variable means duration
t1 = 34  # 1h
t2 = 56  # 1,5h
t3 = 90  # 2h
t4 = 124  # 2,5h
t41 = 123  # 2,5h

# width , how many groups
one__grp = 76
four_grp = 340

# which group
grp = 88

# friday
grpA1_friday = 440
grpA2_friday = grpA1_friday + grp
grpB3_friday = grpA2_friday + grp
grpB4_friday = grpB3_friday + grp

# saturday
grpA1_saturday = 792
grpA2_saturday = grpA1_saturday + grp
grpB3_saturday = grpA2_saturday + grp
grpB4_saturday = grpB3_saturday + grp

# sunday
grpA1_sunday = 1144
grpA2_sunday = grpA1_sunday + grp
grpB3_sunday = grpA2_sunday + grp
grpB4_sunday = grpB3_sunday + grp

# Website URL, it will return current week automatically
url = 'http://plan.ii.us.edu.pl/plan.php?type=2&id=23805&winW=1584&winH=354&loadBG=000000'

# which group should be displayed ?
which_grp = 'B4'

# execute
if __name__ == "__main__":
    ss = ScheduleScraper(url, which_grp)
    ss.execute()
