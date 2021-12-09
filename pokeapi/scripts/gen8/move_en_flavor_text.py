import requests
import bs4
from more_itertools import grouper
import os
from operator import itemgetter
import csv
from time import sleep

if __name__ == "__main__":
    BASE_URL = 'https://bulbapedia.bulbagarden.net'
    MOVE_LIST_URL = BASE_URL + '/wiki/List_of_moves'
    GEN_8 = "VIII"
    GEN_8_ID = "8"

    BULBAPEDIA_ABBREVIATIONS = {
        'SwSh': 20,
        #'BDSP': 21
    }
    ENGLISH_LANGUAGE_ID = 9
    HEADER = ['move_id','version_group_id','language_id','flavor_text']


    response: requests.Response = requests.get(MOVE_LIST_URL)

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    move_list_rows = soup.find_all("tr")

    bulbapedia_gen_8_rows = []

    # Get all gen 8 moves in bulbapedia
    for row in (move_list_rows):
        try:
            rows = row.text.split("\n")
            rows = [x for x in rows if x != '']

            name = rows[1]
            gen = rows[8]

            if (gen == "VIII"):
                move_url = row.find('a').attrs['href']
                bulbapedia_gen_8_rows.append((name, move_url))
        except:
            pass

    bulbapedia_descriptions = []

    for row in (bulbapedia_gen_8_rows):
        sleep(2)

        response = requests.get(BASE_URL + row[1])

        soup = bs4.BeautifulSoup(response.content, "html.parser")

        tables = soup.find_all('table')

        for i, table in tables:
            if "Description" in table.text and "Games" in table.text:
                try:
                    rows = table.text.split("\n")
                    rows = [x for x in rows if x != '']

                    # Rows 0, 1 are the header of the description table.
                    description_and_game = list(grouper(rows[2:], 2))

                    for game, description in description_and_game:
                        game_id = BULBAPEDIA_ABBREVIATIONS[game]

                        bulbapedia_descriptions.append((row[0], game_id, description))
                except:
                    pass

    # Bulbapedia has a weird table inside table thing that makes some entries duplicated
    bulbapedia_descriptions = list(set(bulbapedia_descriptions))

    path = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "..", "..", "data")
    csv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "..", "pokedex", "data", "csv")

    entries = []

    with open(os.path.join(csv_path, "moves.csv"), "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        for row in reader:
            if row[0].isnumeric() and row[2] == GEN_8_ID:
                entries.append([int(row[0]), row[1]])


    entries = dict(entries)
    entries = {v: k for k, v in entries.items()}

    insert_rows = []

    for description in bulbapedia_descriptions:
        name = description[0].lower().replace(" ", "-")
        game_id = description[1]
        text = description[2]

        try:
            insert_rows.append([entries[name], game_id, ENGLISH_LANGUAGE_ID, text])
        except:
            pass

    insert_rows = sorted(insert_rows, key=itemgetter(0))

    with open(os.path.join(csv_path, "move_flavor_text.csv"), "a", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=",")

        writer.writerows(insert_rows)

    