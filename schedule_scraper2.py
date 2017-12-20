# Python 3.6
# Beautiful Soup 4.4
# Requests
#
# schedule_scraper version 2 | Plan zajęć na Uniwersytecie Śląskim
# 17.12.2017 Tomasz Wisniewski

import requests
import re
from bs4 import BeautifulSoup

# CONSTANTS

# Website's URL, it will return schedule table for current week
URL = "http://plan.ii.us.edu.pl/plan.php?type=2&id=23805&winW=1584&winH=354&loadBG=000000"
WEEK = "&w=4"
URL += WEEK

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
GROUP_A2_saturday = GROUP_A1_saturday + COLUMN_GROUP_WIDTH  # 880
GROUP_B3_saturday = GROUP_A2_saturday + COLUMN_GROUP_WIDTH
GROUP_B4_saturday = GROUP_B3_saturday + COLUMN_GROUP_WIDTH

# Sunday
GROUP_A1_sunday = 1144
GROUP_A2_sunday = GROUP_A1_sunday + COLUMN_GROUP_WIDTH  # 1223
GROUP_B3_sunday = GROUP_A2_sunday + COLUMN_GROUP_WIDTH
GROUP_B4_sunday = GROUP_B3_sunday + COLUMN_GROUP_WIDTH


class ScheduleScrapper(object):
    def __init__(self):
        self._time_table = self.create_time_table()
        self._friday_schedule = []
        self._saturday_schedule = []
        self._sunday_schedule = []
        self._url = URL

    def show_time_table(self):
        return self._time_table

    def remove_redundancy(self, schedule_data):
        """Removes duplicates from data"""
        cleaned = []

        for record in schedule_data:
            if record not in cleaned:
                cleaned.append(record)

        return cleaned

    def calculate_top_hour_cords(self, hour, top_cord, height):
        """
        Calculates coordinates from scraped data.

        :param hour: full hour
        :param top_cord: initial value for top variable (scraped from website)
        :param height: height difference between nodes
        :return: list with tuples (coordinates, time)
        """
        result_table = []
        formatted_time = ""
        time_cords = 0

        for multiplier in range(4):
            formatted_time = '{:0>2}:{:0<2}'.format((str(hour)), str(multiplier * 15))
            time_cords = top_cord + height * multiplier

            result_table.append([time_cords, formatted_time])

        next_hour_cords = top_cord + 4 * height + 1
        return result_table, next_hour_cords  # table, next hour's coordinates

    def create_time_table(self):
        """
        Creates time table as dictionary.
        :return: dictionary with time intervals and according coordinates(15 min each)
        """
        time_table = {}
        first_full_hour = 8  # 8:00
        last_full_hour = 22  # last hour 21:00
        hour_cords = 282  # initial value for 8:00
        height_diff = 11  # height difference between nodes (each is equal to 15 min)

        for i in range(first_full_hour, last_full_hour):
            full_hour, hour_cords = self.calculate_top_hour_cords(i, hour_cords, height_diff)
            full_hour = dict(full_hour)
            time_table.update(full_hour)

        return time_table

    def scrap(self):
        """
        Main scrapping procedure. All results will be in :

        self._friday_schedule
        self._saturday_schedule
        self._sunday_schedule

        as sorted lists.
        """

        soup = None

        try:
            web_page = requests.get(self._url)
            soup = BeautifulSoup(web_page.content, "html.parser")

        except Exception as error:
            with open("error_log.txt", "a") as log:
                log.write(str(error) + "\n")
            exit(-1)

        div_tags = soup.find_all("div", class_="coursediv", mtp=True)

        for nr, div_tag in enumerate(div_tags):

            # Extract lecture , teacher , lecture room number
            lecture_info = [text for text in div_tag.stripped_strings]
            lecture_name_and_type = lecture_info[0].split(",")
            del lecture_info[0]
            lecture_info.insert(0, lecture_name_and_type[0])
            lecture_info.insert(1, lecture_name_and_type[1].strip())

            # Extract data rectangle coordinates
            end_of_cords = div_tag.get("style").find("border")
            data_rectangles = div_tag.get("style")[:end_of_cords].replace("\n", "").split(";")
            data_rectangles = [rectangle.strip().replace("px", "") for rectangle in data_rectangles]
            data_rectangles = data_rectangles[:len(data_rectangles) - 1]

            # Example of extracted data as list
            # ['width: 76', 'height: 90', 'top: 394', 'left: 792']

            # Data conversion from list to dictionary with integer values and coordinates
            coordinates = {}
            for data in data_rectangles:
                tmp_data = data.replace(" ", "").split(":")
                coordinates[tmp_data[0]] = int(tmp_data[1])

            # Assign lectures to correct lists based on coordinates:
            # group
            # lecture_info[0] # lecture name
            # lecture_info[1] # type
            # lecture_info[2] # teacher
            # lecture_info[3] # lecture room number
            # coordinates

            # FRIDAY --------------------------------
            if coordinates['left'] == GROUP_A1_friday:
                if coordinates['width'] == WIDTH_ONE_GROUP:
                    self._friday_schedule.append(
                        ["A1", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                elif coordinates["width"] == WIDTH_FOUR_GROUPS:
                    self._friday_schedule.append(
                        ["A1", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                    self._friday_schedule.append(
                        ["A2", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                    self._friday_schedule.append(
                        ["B3", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                    self._friday_schedule.append(
                        ["B4", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])

            if coordinates['left'] == GROUP_A2_friday:
                self._friday_schedule.append(
                    ["A2", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
            if coordinates['left'] == GROUP_B3_friday:
                self._friday_schedule.append(
                    ["B3", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
            if coordinates['left'] == GROUP_B4_friday:
                self._friday_schedule.append(
                    ["B4", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])

            # SATURDAY ------------------------------
            if coordinates['left'] == GROUP_A1_saturday:
                if coordinates['width'] == WIDTH_ONE_GROUP:
                    self._saturday_schedule.append(
                        ["A1", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                elif coordinates["width"] == WIDTH_FOUR_GROUPS:
                    self._saturday_schedule.append(
                        ["A1", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                    self._saturday_schedule.append(
                        ["A2", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                    self._saturday_schedule.append(
                        ["B3", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                    self._saturday_schedule.append(
                        ["B4", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])

            if coordinates['left'] == GROUP_A2_saturday:
                self._saturday_schedule.append(
                    ["A2", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
            if coordinates['left'] == GROUP_B3_saturday:
                self._saturday_schedule.append(
                    ["B3", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
            if coordinates['left'] == GROUP_B4_saturday:
                self._saturday_schedule.append(
                    ["B4", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])

            # SUNDAY ----------------------------------
            if coordinates['left'] == GROUP_A1_sunday:
                if coordinates['width'] == WIDTH_ONE_GROUP:
                    self._sunday_schedule.append(
                        ["A1", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                elif coordinates["width"] == WIDTH_FOUR_GROUPS:
                    self._sunday_schedule.append(
                        ["A1", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                    self._sunday_schedule.append(
                        ["A2", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                    self._sunday_schedule.append(
                        ["B3", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
                    self._sunday_schedule.append(
                        ["B4", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])

            if coordinates['left'] == GROUP_A2_sunday:
                self._sunday_schedule.append(
                    ["A2", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
            if coordinates['left'] == GROUP_B3_sunday:
                self._sunday_schedule.append(
                    ["B3", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])
            if coordinates['left'] == GROUP_B4_sunday:
                self._sunday_schedule.append(
                    ["B4", lecture_info[0], lecture_info[1], lecture_info[2], lecture_info[3], coordinates])

        # Remove redundancy
        self._friday_schedule = self.remove_redundancy(self._friday_schedule)
        self._saturday_schedule = self.remove_redundancy(self._saturday_schedule)
        self._sunday_schedule = self.remove_redundancy(self._sunday_schedule)

        # Sort results by group
        self._friday_schedule = sorted(self._friday_schedule, key=lambda x: x[0])
        self._saturday_schedule = sorted(self._saturday_schedule, key=lambda x: x[0])
        self._sunday_schedule = sorted(self._sunday_schedule, key=lambda x: x[0])


def main():
    scrapper = ScheduleScrapper()
    scrapper.scrap()
    print(scrapper.show_time_table())


if __name__ == "__main__":
    main()
