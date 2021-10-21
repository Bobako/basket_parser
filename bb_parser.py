import sys
import datetime

import requests
from bs4 import BeautifulSoup as Soup
from openpyxl import Workbook


FILENAME:str
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"

url = "https://line4bet.ru/wp-content/themes/twentyseventeen/action_sport.php"


def gen_dates(date=None):
    end_date = datetime.datetime.now().date()
    if not date:
        date = datetime.date(2020, 1, 1)
    else:
        date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
    dates = []
    while date < end_date:
        dates.append(date.strftime("%d-%m-%Y"))
        date += datetime.timedelta(days=1)
    return dates


def parse_day(date_f):
    load = {
        "data_p": date_f,  # day month year
        "sport_p": "basketball",
        "buk_p": "1xstavka"
    }

    a = requests.post(url, data=load, headers={"User-Agent": UA})
    text = a.text
    soup = Soup(text, features="html.parser")

    tables = soup.find_all("table")

    events = []
    error = False
    event = {"date": None,
             "match": [],
             "first": [],
             "second": [],
             "third": [],
             "forth": [],
             "total": [],
             "k": []}
    for table in tables:
        if table.get("class") is None:
            tr = table.find_all("tr")[-2]

            tds = tr.find_all("td")
            event["k"] = tds[1].text, tds[2].text
            if not error:
                events.append(event)
        elif table.get("class")[0] == "liga":
            continue
        elif table.get("class")[0] == "event":
            event = {}
            error = False
            event_text = table.find("td").text
            date, event_text = event_text.split(' ')[0], event_text[17:]
            com1, com2 = event_text[0:event_text.find(" - ")], event_text[event_text.find(" - ") + 3:]
            event["date"] = date
            event["match"] = [com1, com2]

            event_score = table.find_all("td")[2].text
            try:
                event["total"] = event_score.split(" ")[6].split(":")
            except IndexError:
                error = True
            scores = event_score[event_score.find("(") + 1: event_score.find(")")].split(",")
            try:
                event["first"] = scores[0].split(":")
                event["second"] = scores[1].split(":")
                event["third"] = scores[2].split(":")
                event["forth"] = scores[3].split(":")
            except IndexError:
                error = True
    return events


def save_list(wb, list_):
    ws = wb.active
    for event in list_:
        com1 = []
        com2 = []
        for i, value in enumerate(list(event.values())):
            if i:
                com2.append(value[1])
                com1.append(value[0])
            else:
                com1.append(value)
                com2.append("")
        ws.append(com1)
        ws.append(com2)
    wb.save(FILENAME)


def create_wb(name):
    wb = Workbook()
    ws = wb.active
    ws.append(["Дата", "матч", "счет 1 партии", "счет 2 партии", "счет 3 партии", "счет 4 партии", "итого счет матча",
               "коэффициент перед началом матча в букмекерax"])

    global FILENAME
    FILENAME = f"./{name}.xlsx"
    wb.save(FILENAME)
    return wb

if __name__ == '__main__':
    if len(sys.argv) == 2:
        start_date = sys.argv[1]
    else:
        start_date = None
    dates = gen_dates(start_date)
    print(f"Парсинг с {dates[0]} по сегодняшний день")
    wb = create_wb(f"basketball_{dates[0]}---{dates[-1]}")
    l = len(dates)
    for i, date in enumerate(dates):
        print(f"{i}/{l}({date}.....)")
        list_ = parse_day(date)
        save_list(wb, list_)
    print("Готово.")


