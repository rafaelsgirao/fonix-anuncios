import json
import requests

from dotenv import load_dotenv
load_dotenv()

from os import getenv

f = open("link_map.json", "r", encoding="utf-8")
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
    template = """<p><input type=checkbox name={degree} value='{uc}'> ({uc}) {uc_name}<br/></p>"""

    for degree in data:
        print("        <h2>{}</h2>".format(degree))
        #a button with a type named 'button' seems stupid but welp, it works
        print('        <button type="button" class="collapsible">Abrir </button>')
        print('        <div class="content">')

        for uc in data[degree]:
            #print(f"{uc} - {course} | Fónix Anúncios")
            #print(create_mailing_list(course, uc))
            print(template.format(degree=degree, uc=uc, uc_name=data[degree][uc]["name"]))
        print('        </div>')

#print(data)
#for degree in data:
    #for uc in data[degree]:
        #print(uc)
        
        #print(f"{data[degree][uc]['name']} - {degree} | Fónix Anúncios")
        #print(create_mailing_list(degree, uc))

def gen_r2e_cmds(data):
    for degree in data:
        for uc in data[degree]:
            address = f'{degree.lower()}-{uc.lower()}-anuncios@mg.rafael.ovh'
            print(f"./r2e add {degree}-{uc}-Anuncios {data[degree][uc]['link']} {address}")