from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import Form
from wtforms import TextField, BooleanField
from uuid import uuid4
import json
app = Flask(__name__)

app.config['SECRET_KEY'] = 'DaRshLqsK7TVjgUUXHoQSRnmMfQn6orDeAxjLEaGPdGqF2wdKwuCkzpdwXvQdadX'

def load_cfg():
    global cfg
    with open("conf.json", "r+", encoding="utf-8") as f:
        cfg = json.load(f)

def dump_cfg():
    global cfg
    with open("conf.json", "w+", encoding="utf-8") as f:
        f.seek(0)
        f.truncate()
        json.dump(cfg, f, indent=4, ensure_ascii=False)

    print("Dumped to file 'dirs.json'")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register-done')
def register_done():
    return render_template('register-done.html')

@app.route('/confirm/<token>')
def confirm(token):
    global cfg
    token_found=False
    print(cfg.items())
    for email_cfg, token_cfg in cfg.items():
        if token == token_cfg:
            print("yes")
            token_found=True
            cfg.pop(email_cfg)
            dump_cfg()
            header = "Obrigado por confirmares!"
            text = f"O teu e-mail {email_cfg} confirmado. Já deves começar a receber os próximos anúncios neste e-mail."
            return render_template('info.html', text=text, header=header)
    if not token_found:

        text = 'ERRO: Token Inválido.'
        return render_template('info.html', text=text)

# Simple form handling using raw HTML forms
@app.route('/register', methods=['GET', 'POST'])
def sign_up():
    global cfg
    error = ""
    if request.method == 'POST':
        # Form being submitted; grab data from form.
        #leic_a = request.form.getlist('leic-a')
        data = request.form.to_dict()
        #last_name = request.form['lastname']
        print(data)
        # Validate form data
        if len(data) == 0:
            # Form data failed validation; try again
            error = "ERRO: Tens que selecionar alguma coisa"
        else:
            # Form data is valid; move along
            cfg[data["email"]] = str(uuid4())
            dump_cfg()
            return redirect(url_for('register_done'))

    # Render the sign-up page
    return render_template('sign-up.html', message=error)


load_cfg()    
app.run(debug=True)
