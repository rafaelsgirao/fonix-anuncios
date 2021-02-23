import json
import requests
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
        auth=('api', 'key-80b486670c968b16bfb2e1c7db703317'),
        data={'address': address,
              'description': description,
              'reply_preference': 'sender'
        }).text

template = """<p><input type=checkbox name={course} value='{uc}'> {uc_high} <br/></p>"""

for course in data:
    print("        <h2>{}</h2>".format(course))
    print('        <button onclick="return false;" class="collapsible">Abrir </button>')
    print('        <div class="content">')

    for uc in data[course]:
        if data[course][uc] != "":
            #print(f"{uc} - {course} | Fónix Anúncios")
            #print(create_mailing_list(course, uc))
            print(template.format(course=course.lower(), course_high=course, uc=uc.lower(), uc_high=uc))
    print('        </div>')