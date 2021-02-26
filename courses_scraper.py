import requests
import re
import json

#Stolen from https://github.com/ist-bot-team/ist-discord-bot, sue me
#This a very dirty mod from the version of the script above, but hey, it works

# Intervalo [since,until[ de pares (Ano,Semestre) para dar scrapping
# Provavelmente nada robusto mas há que ter fé
since = [1, 2]
until = [2, 1]


def scrape_degree(degree):
    html = requests.get(
        'https://fenix.tecnico.ulisboa.pt/cursos/{}/curriculo'.format(
            degree)).text
    start = html.find('<h4>Ano {}, Semestre {}</h4>'.format(*since))
    end = html.find('<h4>Ano {}, Semestre {}</h4>'.format(*until))
    courses = re.findall(r'>(.*)\s<\/a>', html[start:end])
    return courses


course_acronym_map = {}
link_map = {}

def add_all_courses_from_degree(degree):
    degree_id = degree['id']
    degree_acronym = degree['acronym']

    global course_acronym_map
    global link_map

    if degree_acronym not in link_map:
        link_map[degree_acronym] = {}

    courses = requests.get(
        'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/degrees/{}/courses?academicTerm=2020/2021'
        .format(degree_id)).json()

    for course in courses:
        acronym = re.match(".*?([A-Za-z]+)\d*",
                           course['acronym']).groups()[0].lower()
        trailingRomanNumeral = re.search(" (III|II|I|IV|V|VIII|VII|VI|)$",
                                         course['name'])
        if trailingRomanNumeral:
            acronym += '-{}'.format(
                trailingRomanNumeral.groups()[0].lower())
        course_acronym_map[course['name']] = acronym
        link = f"https://fenix.tecnico.ulisboa.pt/disciplinas/{course['acronym']}/2020-2021/2-semestre/rss/announcement"
        link_map[degree_acronym][acronym] = {'name': course['name'], 'link': link}

all_degrees = requests.get(
    'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/degrees?academicTerm=2020/2021'
).json()
degrees = list(
    filter(
        lambda degree: degree['type'] in
        ['Licenciatura Bolonha', 'Mestrado Integrado'], all_degrees))

#print(degrees)

link_map_filtered = {}
degree_courses = {}

for degree in degrees:
   # if degree['name'] not in rslt:
        #rslt[degree]['acronym'] = {}

    add_all_courses_from_degree(degree)

    courses = scrape_degree(degree['acronym'].lower())

    link_map_filtered[degree['acronym']] = {}



    for course in courses:
        acronym = course_acronym_map[course]
        if acronym not in degree_courses:
            degree_courses[acronym] = {'name': course, 'degrees': []}
        degree_courses[acronym]['degrees'].append(degree['acronym'])

        #link map
       # print(f"degree: {degree['acronym']}, course: {acronym}")
        link_map_filtered[degree['acronym']][acronym] = link_map[degree['acronym']][acronym] 

#Remap old course names to new ones

link_map_filtered['LETI'] = link_map_filtered.pop('LERC')
link_map_filtered['LENO'] = link_map_filtered.pop('LEAN')        

#print(link_map)
#with open('courses_by_degree.json', 'wb') as file:
#    file.write(
#        json.dumps(degree_courses, ensure_ascii=False,
#                   sort_keys=True).encode('utf-8'))
#    file.close()

with open('link_map.json', 'wb') as file:
    file.write(
        json.dumps(link_map_filtered, ensure_ascii=False,
                   sort_keys=True, indent=4).encode('utf-8'))
    file.close()
#print(rslt)