import json
import requests

from dotenv import load_dotenv
load_dotenv()

from os import getenv

f = open("courses_by_degree.json", "r", encoding="utf-8")
data = json.load(f)
f.close()
#print(data)

def create_mailing_list(course, uc):
    address = f'{course.lower()}-{uc.lower()}-anuncios@mg.rafael.ovh'
    description = f"Receber anúncios de {uc} para {course}"
    print(address)
    print(description)
    return requests.post(
        "https://api.eu.mailgun.net/v3/lists",
        auth=('api', getenv('MAILGUN_API_KEY')),
        data={'address': address,
              'description': description,
              'reply_preference': 'sender'
        }).text

def make_template(data):
    template = """<p><input type=checkbox name={course} value='{uc}'> {uc} <br/></p>"""

    for course in data:
        print("        <h2>{}</h2>".format(course))
        print('        <button onclick="return false;" class="collapsible">Abrir </button>')
        print('        <div class="content">')

        for uc in data[course]:
            if data[course][uc] != "":
                #print(f"{uc} - {course} | Fónix Anúncios")
                #print(create_mailing_list(course, uc))
                print(template.format(course=course, uc=uc))
        print('        </div>')

for course in data:
    for uc in data[course]:
        if data[course][uc] != "":
            print(f"{uc} - {course} | Fónix Anúncios")
            #print(create_mailing_list(course, uc))

def gen_r2e_cmds(data):
    for course in data:
        for uc in data[course]:
            if data[course][uc] != "":
                address = f'{course.lower()}-{uc.lower()}-anuncios@mg.rafael.ovh'
                print(f"./r2e add {course}-{uc}-Anuncios {data[course][uc]} {address}")