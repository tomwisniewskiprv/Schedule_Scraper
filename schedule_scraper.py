# -*- coding: utf-8 -*-
"""
    schedule_scraper.py

    Script scrapes web page content for schedule.

    Python 3.6
    10.06.2017 Tomasz Wisniewski
"""
import time
import requests
from bs4 import BeautifulSoup


# ------------ measure time
t0 = time.clock()

def calculate_top_cord_for_hour(h, top_cord, top_jump):
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


def create_time_table():
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
        tmp_tab, top_next_hour = calculate_top_cord_for_hour(i, top_next_hour, top_jump)
        d = dict(tmp_tab)
        time_table.update(d)

    return time_table


# legend
teachers = { 'MCh': 'Marcin Cholewa',
             'ASa': 'Arkadiusz Sacewicz',
             'PP' : 'Piotr Paszek',
             'PG' : 'Paweł Gładki',
             'MB' : 'Barbara M. Paszek',
             'MaPa' : 'Małgorzata Pałys',
             'LA' : 'Aleksander Lamża',
             'TK' : 'Katarzyna Trynda',
             'KP' : 'Przemysław Kudłacik',
             'EK-W' : 'Ewa Karolczak-Wawrzała',

             }

# All variables needed for correct data interpretation
# height variable means length of classes
t1 = 34  # 1h
t2 = 56  # 1,5h
t3 = 90  # 2h

t4 = 124  # 2,5h
t41 = 123 # 2,5h

# width , how many groups
one__grp = 76
four_grp = 340

# which group
grp1 = 88
grp2 = grp1 * 2
grp3 = grp1 * 3
grp4 = grp1 * 4

# friday
grpA1_friday = 440
grpA2_friday = grpA1_friday + grp1
grpB1_friday = grpA2_friday + grp1
grpB2_friday = grpB1_friday + grp1

# saturday
grpA1_saturday = 792
grpA2_saturday = grpA1_saturday + grp1
grpB1_saturday = grpA2_saturday + grp1
grpB2_saturday = grpB1_saturday + grp1

# sunday
grpA1_sunday = 1144
grpA2_sunday = grpA1_sunday + grp1
grpB1_sunday = grpA2_sunday + grp1
grpB2_sunday = grpB1_sunday + grp1

# Scraped data storage
time_table = create_time_table()
friday = []
saturday = []
sunday = []

# url = 'http://plan.ii.us.edu.pl/plan.php?type=2&id=23805&w=36&bw=0&winW=1584&winH=720&loadBG=000000'
url = 'http://plan.ii.us.edu.pl/plan.php?type=2&id=23805&w=46&winW=1584&winH=354&loadBG=000000'
# url = 'http://plan.ii.us.edu.pl/plan.php?type=2&id=23805&w=36&bw=0&winW=1584&winH=720&loadBG=000000'


# Actual scraping
data = requests.get(url)
soup = BeautifulSoup(data.content, 'html.parser')
parsed = soup.prettify()

tags_id = soup.find_all('div', class_='coursediv')
"""
This for loop below is very specially tailored to handle very ugly source code from website.
Aka Main Loop () 
"""
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

        """
        MEMO :
        Source code from website has bugs. Some entries are doubled or tripled. I had decided to deal with
        redundant data in function clean_results which will work on data sorted by group.
        
        I'm aware of this problem.
        """

        if coordinates['left'] == grpA1_friday:
            if coordinates['width'] == one__grp:
                friday.append(['A1', subject, tutor, room, coordinates])
            elif coordinates['width'] == four_grp:
                friday.append(['A1', subject, tutor, room, coordinates])
                friday.append(['A2', subject, tutor, room, coordinates])
                friday.append(['B1', subject, tutor, room, coordinates])
                friday.append(['B2', subject, tutor, room, coordinates])
        if coordinates['left'] == grpA2_friday:
            friday.append(['A2', subject, tutor, room, coordinates])
        if coordinates['left'] == grpB1_friday:
            friday.append(['B1', subject, tutor, room, coordinates])
        if coordinates['left'] == grpB2_friday:
            friday.append(['B2', subject, tutor, room, coordinates])

        if coordinates['left'] == grpA1_saturday:
            if coordinates['width'] == one__grp:
                saturday.append(['A1', subject, tutor, room, coordinates])
            elif coordinates['width'] == four_grp:
                saturday.append(['A1', subject, tutor, room, coordinates])
                saturday.append(['A2', subject, tutor, room, coordinates])
                saturday.append(['B1', subject, tutor, room, coordinates])
                saturday.append(['B2', subject, tutor, room, coordinates])
        if coordinates['left'] == grpA2_saturday:
            saturday.append(['A2', subject, tutor, room, coordinates])
        if coordinates['left'] == grpB1_saturday:
            saturday.append(['B1', subject, tutor, room, coordinates])
        if coordinates['left'] == grpB2_saturday:
            saturday.append(['B2', subject, tutor, room, coordinates])

        if coordinates['left'] == grpA1_sunday:
            if coordinates['width'] == one__grp:
                sunday.append(['A1', subject, tutor, room, coordinates])
            elif coordinates['width'] == four_grp:
                sunday.append(['A1', subject, tutor, room, coordinates])
                sunday.append(['A2', subject, tutor, room, coordinates])
                sunday.append(['B1', subject, tutor, room, coordinates])
                sunday.append(['B2', subject, tutor, room, coordinates])
        if coordinates['left'] == grpA2_sunday:
            sunday.append(['A2', subject, tutor, room, coordinates])
        if coordinates['left'] == grpB1_sunday:
            sunday.append(['B1', subject, tutor, room, coordinates])
        if coordinates['left'] == grpB2_sunday:
            sunday.append(['B2', subject, tutor, room, coordinates])


"""
At this point I have data scraped. Now I have to sort it out and then display data in nice format.
"""


def sort_data(data):
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


def sort_day_by_grp(data, grp):
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


def clean_results(data):
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


friday_sorted = sort_data(friday)
saturday_sorted = sort_data(saturday)
sunday_sorted = sort_data(sunday)

current_grp = 'A1'

friday_sorted_by_grp = sort_day_by_grp(friday, current_grp)
friday_sorted_by_grp = clean_results(friday_sorted_by_grp)

saturday_sorted_by_grp = sort_day_by_grp(saturday_sorted, current_grp)
saturday_sorted_by_grp = clean_results(saturday_sorted_by_grp)

sunday_sorted_by_grp = sort_day_by_grp(sunday_sorted, current_grp)
sunday_sorted_by_grp = clean_results(sunday_sorted_by_grp)


# Display the results

with open('schedule.txt', 'w')as fout:
    fout.write('FRIDAY:\n')
    for lesson in friday_sorted_by_grp:
        print(time_table[lesson[4]['top']], lesson[0], lesson[1], teachers.get(lesson[2][0]))
        fout.writelines('{} {} {} {}\n'.format(time_table[lesson[4]['top']], lesson[0], lesson[1], teachers.get(lesson[2][0])))

    fout.write('SATURDAY:\n')
    for lesson in saturday_sorted_by_grp:
        print(time_table[lesson[4]['top']], lesson[0], lesson[1], teachers.get(lesson[2][0]))
        fout.writelines('{} {} {} {}\n'.format(time_table[lesson[4]['top']], lesson[0], lesson[1], teachers.get(lesson[2][0])))

    fout.write('SUNDAY:\n')
    for lesson in sunday_sorted_by_grp:
        print(time_table[lesson[4]['top']], lesson[0], lesson[1], teachers.get(lesson[2][0]))
        fout.writelines('{} {} {} {}\n'.format(time_table[lesson[4]['top']], lesson[0], lesson[1], teachers.get(lesson[2][0])))


# ------------ measure time
t00 = time.clock()
print('time', t00 - t0)

# the end
