import re
from requests import post
from flask import Flask, render_template, request, redirect, url_for, escape
# from flask_wtf import Form
# from wtforms import TextField, BooleanField
from uuid import uuid4
import json

from os import getenv
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

import sys
EMAIL_EXPR = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

f = open("link_map.json", "r", encoding="utf-8")
#Load Courses By Degree
cbd = json.load(f)
f.close()

# Todo: Regen and load this from .env file
app.config['SECRET_KEY']=getenv('FLASK_SECRET_KEY')

@app.after_request
def add_security_headers(resp):
    resp.headers['Content-Security-Policy'] = "default-src 'self'"
    resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    resp.headers['X-XSS-Protection'] = '1; mode=block'
    return resp

def send_confirmation_email(email, link):
    return post(
        f"https://api.eu.mailgun.net/v3/{getenv('MAILGUN_DOMAIN')}/messages",
        auth=("api", getenv("MAILGUN_API_KEY")),

        data={"from": f"Fónix Anúncios <fonix-notifications@{getenv('MAILGUN_DOMAIN')}>",
              "to": [email],
              "subject": "Fónix Anúncios | Confirma o teu e-mail",
              "text": f"Olá! Carrega no link abaixo para confirmares o teu e-mail.\n{link} \n Se não foste tu a pedir este e-mail podes ignorá lo."}).text

def add_list_member(email, mailing_lists):
    responses = []
    for mailing_list in mailing_lists:
        responses.append(post(
            f"https://api.eu.mailgun.net/v3/lists/{mailing_list}/members.json",
            auth=("api", getenv("MAILGUN_API_KEY")),
            data={'upsert': True,
                'members': f'[{{"address": "<{email}>"}}]'}).text)
    return responses

    
def check_email(email):
    global EMAIL_EXPR
    return bool(re.search(EMAIL_EXPR, email))

def load_cfg():
    global cfg
    with open("conf.json", "r+", encoding="utf-8") as f:
        cfg=json.load(f)

def dump_cfg():
    global cfg
    with open("conf.json", "w+", encoding="utf-8") as f:
        f.seek(0)
        f.truncate()
        json.dump(cfg, f, indent=4, ensure_ascii=False)

    print("Dumped to file 'conf.json'")

@ app.route('/')
def index():
    #return render_template('index.html')
    return redirect(url_for('register'))

@ app.route('/register-done')
def register_done():
    return render_template('register-done.html')

@ app.route('/confirm/<token>')
def confirm(token):
    global cfg
    global cbd
    token_found=False
    for email in cfg:
        if cfg[email]["token"] == token:
            token_found=True

            print(add_list_member(email, cfg[email]["subscriptions"]))
            cfg.pop(email)
            dump_cfg()
            header="Obrigado por confirmares!"
            text=f"O teu e-mail {email} confirmado. Já deves começar a receber os próximos anúncios."
            return render_template('confirm.html', text=text, header=header)
    if not token_found:
        header = "Erro"
        text='Token Inválido (provavelmente já validaste o teu e-mail?).'
        return render_template('confirm.html', text=text, header=header)

# Simple form handling using raw HTML forms
@ app.route('/register', methods=['GET', 'POST'])
def register():
    global cfg
    text = ""
    if request.method == 'POST':
        # Form being submitted; grab data from form.
        email=escape(request.form['email'])


        form_data_correct = True
        #loop through every course in courses by degree
        #pretty sure there's a better way to do this
        subscriptions = []
        for course in cbd:
            selected_degrees = request.form.getlist(course)
            if len(selected_degrees) == 0:
                continue 
            for degree in selected_degrees:
                if degree not in cbd[course]:
                    text = f"ERRO: Cadeira '{degree}'' inválida em '{course}''."
                    form_data_correct = False
                    break
                elif cbd[course][degree] == "":
                    form_data_correct = False
                    text = f"ERRO: Cadeira '{degree}'' inválida em '{course}''."
                    break
                else:
                    subscriptions.append(f"{course.lower()}-{degree.lower()}-anuncios@{getenv('MAILGUN_DOMAIN')}")
        print(subscriptions)
        print(len(subscriptions))
        if len(subscriptions) == 0:
            text = "ERRO: Tens que selecionar alguma coisa!"
            form_data_correct = False
        form_data_correct = True

        # Validate form data
        if not check_email(email):
            text = "ERRO: Email inválido."
        elif not form_data_correct:
            text = "ERRO: Disciplinas e/ou curso inválidas."
        else:
            # Form data is valid; move along
            token = str(uuid4())
            #cfg[email]=token
            cfg[email]= {
                "token": token,
                "subscriptions": subscriptions
            }
            dump_cfg()
            #Get current link without request path, e.g http://localhost:5000
            base_link = request.base_url[:-len(request.path)]
            
            link = base_link + url_for("confirm", token=token)
            print(send_confirmation_email(email, link))
            return redirect(url_for('register_done'))

    # Render the sign-up page
    return render_template('register.html', message=text)


load_cfg()
if __name__=="__main__":
    app.run(debug=True)
