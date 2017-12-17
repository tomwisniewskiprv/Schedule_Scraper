# Python 3.6
# US_plan | main
# 17.12.2017 Tomasz Wisniewski

import requests
from bs4 import BeautifulSoup

# CONSTANTS

# Website's URL, it will return schedule for current week automatically
URL = "http://plan.ii.us.edu.pl/plan.php?type=2&id=23805&winW=1584&winH=354&loadBG=000000"

# Height variable means duration
HEIGHT_TIME_1h = 34  # 1h
HEIGHT_TIME_1_5h = 56  # 1,5h
HEIGHT_TIME_2h = 90  # 2h
HEIGHT_TIME_2_5ha = 124  # 2,5h
HEIGHT_TIME_2_5hb = 123  # 2,5h

# Block width which means how many groups are affected
WIDTH_ONE_GROUP = 76
WIDTH_FOUR_GROUPS = 340

# Which group
COLUMN_GROUP_WIDTH = 88

# Friday
GROUP_A1_friday = 440
GROUP_A2_friday = GROUP_A1_friday + COLUMN_GROUP_WIDTH  # 528
GROUP_B3_friday = GROUP_A2_friday + COLUMN_GROUP_WIDTH
GROUP_B4_friday = GROUP_B3_friday + COLUMN_GROUP_WIDTH

# Saturday
GROUP_A1_saturday = 792
GROUP_A2_saturday = GROUP_A1_saturday + COLUMN_GROUP_WIDTH # 880
GROUP_B3_saturday = GROUP_A2_saturday + COLUMN_GROUP_WIDTH
GROUP_B4_saturday = GROUP_B3_saturday + COLUMN_GROUP_WIDTH

# Sunday
GROUP_A1_sunday = 1144
GROUP_A2_sunday = GROUP_A1_sunday + COLUMN_GROUP_WIDTH # 1223
GROUP_B3_sunday = GROUP_A2_sunday + COLUMN_GROUP_WIDTH
GROUP_B4_sunday = GROUP_B3_sunday + COLUMN_GROUP_WIDTH


class ScheduleScrapper(object):
    def __init__(self):
        self._time_table = []
        self._friday = []
        self._saturday = []
        self._sunday = []
        self._url = URL

    def calculate_top_cord_for_hour(self, hour, top_cord, top_jump):
        """
        Calculates coordinates from scraped data.

        :param h: full hour
        :param top_cord: initial value for top variable (scraped from website)
        :param top_jump: height difference between nodes
        :return: list with tuples (coordinates, time)
        """
        table = []
        time_str = ""
        time_cords = 0

        for i in range(4):
            if i % 4 == 0:
                time_str = '{:0>2}:{:0<2}'.format((str(hour)), str(i * 15))
                time_cords = top_cord
            if i % 4 == 1:
                time_str = '{:0>2}:{:0<2}'.format((str(hour)), str(i * 15))
                time_cords = top_cord + top_jump
            if i % 4 == 2:
                time_str = '{:0>2}:{:0<2}'.format((str(hour)), str(i * 15))
                time_cords = top_cord + 2 * top_jump
            if i % 4 == 3:
                time_str = '{:0>2}:{:0<2}'.format((str(hour)), str(i * 15))
                time_cords = top_cord + 3 * top_jump

            table.append([time_cords, time_str])

        next_hour_cords = top_cord + 4 * top_jump + 1
        return table, next_hour_cords # table, next hour's coordinates

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


def main():
    print("Main.")
    scrapper = ScheduleScrapper()
    t = scrapper.create_time_table()
    print(t)


if __name__ == "__main__":
    main()
