import pprint
from todoist_api_python.api import TodoistAPI
import obsws_python as obs
import datetime
import schedule
import time
import os

import lib
from lib.data import ParaData

todoist_api = TodoistAPI(lib.todoist_key)
try:
    recorder = obs.ReqClient(
        host="localhost", port=4455, password="Fu2Xfs5vMePGSIkR", timeout=3
    )
except:
    obs_path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OBS Studio\OBS Studio (64bit).lnk"
    os.startfile(obs_path)
    recorder = obs.ReqClient(
        host="localhost", port=4455, password="Fu2Xfs5vMePGSIkR", timeout=3
    )


def reschedule_paras():
    os.system("cls")
    schedule.clear()
    schedule_paras()


def get_scheduled_paras():
    return [
        task
        for task in todoist_api.get_tasks()
        if task.due
        and task.due.date == time.strftime("%Y-%m-%d")
        and len(task.content) == 4
        and " " in task.content
        and ("P" in task.content.upper() or "L" in task.content.upper())
    ]


def schedule_paras():
    scheduled_paras = get_scheduled_paras()
    if not scheduled_paras:
        exit()

    def get_earlier_time(time: str):
        BEFORE_MINTES = 3

        hour, minute = time.split(":")
        return f"{hour}:{int(minute)-BEFORE_MINTES:0>2}"

    for para_data in scheduled_paras:
        para_kind, para_name = para_data.content.split(" ")
        para_kind, para_name = para_kind.upper(), para_name.upper()
        para_scheduled_time = para_data.due.string.split()[-1]
        print(
            f"{lib.get_full_para_kind(para_kind)} {para_name} o {para_scheduled_time}"
        )

        earlier_time: str = get_earlier_time(para_scheduled_time)
        para_abbreviation: str = f"{para_kind} {para_name}"
        schedule.every().day.at(earlier_time).do(open_para, para_abbreviation)
        schedule.every().day.at(para_scheduled_time).do(open_para, para_abbreviation)


def open_para(para_abbr: str = "L IV"):
    def get_time(m) -> str:
        return (datetime.datetime.now() + datetime.timedelta(minutes=m)).strftime(
            "%H:%M"
        )

    def make_paras_data():
        target_file_path = os.path.join(
            r"E:\Notatnyk\Університет\20250828210536 41 Інформація про курси - посилання на заняття, список завдань та викладачів з дисциплін.md"
        )
        paras: list[ParaData] = list()

        with open(target_file_path, encoding="utf-8", mode="r") as f:
            lines = f.readlines()

        for line in lines:
            clean_line = line[2:].strip()
            para: ParaData = ParaData(*clean_line.split(" - "))
            paras.append(para)

        return paras

    CLASS_DURATION_MINUTES: int = 80
    HOW_LONG_TO_RECORD_FOR: int = CLASS_DURATION_MINUTES + 10

    this_class_data: ParaData = [d for d in make_paras_data() if d.name == para_abbr][0]

    os.system(f'start "" {this_class_data.link}')
    lib.copy_text(this_class_data.code) if this_class_data.code else None

    try:
        recorder.start_record()
    except Exception as e:
        print(e)

    time_difference_from_now: str = get_time(HOW_LONG_TO_RECORD_FOR)
    schedule.every().day.at(time_difference_from_now).do(close_para, para_abbr)
    schedule.every().day.at(time_difference_from_now).do(reschedule_paras)


def move_recording_to_its_folder(para_abbr: str = "L PR"):
    def get_latest_file():
        recordings_folder_path = os.path.join(lib.recordings_folder)
        file_paths = [
            os.path.join(recordings_folder_path, file_name)
            for file_name in os.listdir(recordings_folder_path)
            if "." in file_name
        ]
        latest_file = max(file_paths, key=os.path.getmtime)
        return latest_file

    kind, name = para_abbr.split(" ")

    latest_file_path = get_latest_file()
    file_name = latest_file_path.split("\\")[-1]
    moved_file_path = os.path.join(lib.recordings_folder, name, kind, file_name)
    os.replace(latest_file_path, moved_file_path)


def close_para(para_abbr: str = "L IV"):
    try:
        recorder.stop_record()
        time.sleep(10)
    except:
        print("Failed to stop recording")
    move_recording_to_its_folder(para_abbr)


def main():
    reschedule_paras()
    while 1:
        schedule.run_pending()
        time.sleep(40)


ts = [t.content for t in todoist_api.get_tasks()]
pprint.pprint(ts)
