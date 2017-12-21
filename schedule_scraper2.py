# Python 3.6
# Beautiful Soup 4.4
# Requests
#
# schedule_scraper version 2 | Plan zajęć na Uniwersytecie Śląskim
# 17.12.2017 Tomasz Wisniewski

import requests
from bs4 import BeautifulSoup

# CONSTANTS

# Website's URL, it will return schedule table for current week
URL = "http://plan.ii.us.edu.pl/plan.php?type=2&id=23805&winW=1584&winH=354&loadBG=000000"
WEEK_PARAM = "&w="
WEEK = "16"
URL += WEEK_PARAM + WEEK

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
        self._time_table = self._create_time_table()
        self._friday_schedule = []
        self._saturday_schedule = []
        self._sunday_schedule = []
        self._url = URL

        self._get_page_content()

        self._numbered_weeks = {}
        self._current_week = ""

        self._teachers = {'MCh': 'Marcin Cholewa',
                          'ASa': 'Arkadiusz Sacewicz',
                          'PP': 'Piotr Paszek',
                          'PG': 'Paweł Gładki',
                          'MB': 'Barbara M. Paszek',
                          'MaPa': 'Małgorzata Pałys',
                          'LA': 'Aleksander Lamża',
                          'TK': 'Katarzyna Trynda',
                          'KP': 'Przemysław Kudłacik',
                          'EK-W': 'Ewa Karolczak-Wawrzała',
                          'BM': 'Boryczka Mariusz',

                          'ŚM': 'Maciej Ślęczka',
                          'AB': 'Anna Bień',
                          'AH-K': 'Aneta Hanc-Kuczkowska',
                          'PJa': 'Paweł Janik',
                          'BPł': 'Bartłomiej Płaczek',
                          'BR': 'Romuald Błaszczyk',
                          'KSt': 'Kazimierz Stróż',
                          'CM': 'Miłosław Chodacki',
                          }

    def _get_page_content(self):
        """
        Function requests and loads web content.
        It should be used during initialisation of scraper object.
        """
        try:
            self._web_page = requests.get(self._url)
        except Exception as error:
            with open("error_log.txt", "a") as log:
                log.write(str(error) + "\n")

        soup = BeautifulSoup(self._web_page.content, 'html.parser')
        select_tag = soup.find_all('select', id='wBWeek')

        values_weeks = []
        for options in select_tag:
            option = options.find_all('option')

            for week in option:
                values_weeks.append((week.get('value'), week.get_text()))

        self._numbered_weeks = dict(values_weeks)
        self._current_week = self._numbered_weeks.get(WEEK)
        # debug
        print("Schedule for week : ", self._current_week)

    def load_numbered_weeks(self):
        """Returns weeks and corresponding numbers as dictionary"""
        return self._numbered_weeks

    # debug
    def _show_time_table(self):
        print(self._time_table)

    def _remove_redundancy(self, schedule_data):
        """
        Removes duplicates from scrapped data because some data blocks have more then one layer
        describing one data block, so this function is a must.
        """
        cleaned = []

        for record in schedule_data:
            if record not in cleaned:
                cleaned.append(record)

        return cleaned

    def _calculate_top_hour_cords(self, hour, top_cord, height):
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

    def _create_time_table(self):
        """
        Creates time table as dictionary.
        :return: dictionary with time intervals and according coordinates(15 min each)
        """
        time_table = {}
        first_full_hour = 8  # 8:00
        last_full_hour = 22  # last hour 21:00
        hour_cords = 282  # initial value for 8:00
        height_diff = 11  # height difference between nodes (each is equal to 15 min)

        for hour in range(first_full_hour, last_full_hour):
            full_hour, hour_cords = self._calculate_top_hour_cords(hour, hour_cords, height_diff)
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
            soup = BeautifulSoup(self._web_page.content, "html.parser")

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

            if len(lecture_info) < 4:
                lecture_info.append("Brak sali")

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
        self._friday_schedule = self._remove_redundancy(self._friday_schedule)
        self._saturday_schedule = self._remove_redundancy(self._saturday_schedule)
        self._sunday_schedule = self._remove_redundancy(self._sunday_schedule)

        # Sort results by group
        self._friday_schedule = sorted(self._friday_schedule, key=lambda x: x[0])
        self._saturday_schedule = sorted(self._saturday_schedule, key=lambda x: x[0])
        self._sunday_schedule = sorted(self._sunday_schedule, key=lambda x: x[0])

    def _order_results_by_group(self, scraped_data, wanted_group):
        results = []
        for lecture in scraped_data:
            if lecture[0] == wanted_group:
                results.append(lecture)

        results = sorted(results, key=lambda x: x[5]["top"])
        return results

    def get_schedule_for_group(self, wanted_group):
        """ Sorts data to correct order and format
            :returns sorted list # TODO for now
        """

        schedule = []

        friday_schedule = self._order_results_by_group(self._friday_schedule, wanted_group)
        saturday_schedule = self._order_results_by_group(self._saturday_schedule, wanted_group)
        sunday_schedule = self._order_results_by_group(self._sunday_schedule, wanted_group)

        # Friday
        schedule.append("FRIDAY")
        for lecture in friday_schedule:
            teacher = self._teachers.get(lecture[3])
            duration = self._time_table.get(lecture[5]["height"] + lecture[5]["top"] + 12)
            if duration is None:
                duration = self._time_table.get(lecture[5]["height"] + lecture[5]["top"] + 11)
            formatted = "{:5} {:5} {:<5} {:<10} {:<15}".format(self._time_table[lecture[5]["top"]],
                                                               duration,
                                                               lecture[0], lecture[1], teacher)

            schedule.append(formatted)

        # Saturday
        schedule.append("SATURDAY")
        for lecture in saturday_schedule:
            teacher = self._teachers.get(lecture[3])
            duration = self._time_table.get(lecture[5]["height"] + lecture[5]["top"] + 12)
            if duration is None:
                duration = self._time_table.get(lecture[5]["height"] + lecture[5]["top"] + 11)
            formatted = "{:5} {:5} {:<5} {:<10} {:<15}".format(self._time_table[lecture[5]["top"]],
                                                               duration,
                                                               lecture[0], lecture[1], teacher)

            schedule.append(formatted)

        # Sunday
        schedule.append("SUNDAY")
        for lecture in sunday_schedule:
            teacher = self._teachers.get(lecture[3])
            duration = self._time_table.get(lecture[5]["height"] + lecture[5]["top"] + 12)
            if duration is None:
                duration = self._time_table.get(lecture[5]["height"] + lecture[5]["top"] + 11)
            formatted = "{:5} {:5} {:<5} {:<10} {:<15}".format(self._time_table[lecture[5]["top"]],
                                                               duration,
                                                               lecture[0], lecture[1], teacher)

            schedule.append(formatted)

        return schedule

    def show_schedule_for_group(self, group):
        # DEBUG
        for x in self.get_schedule_for_group(group):
            print(x)


def main():
    scrapper = ScheduleScrapper()
    scrapper.scrap()
    scrapper.show_schedule_for_group("A1")


if __name__ == "__main__":
    main()
