# FP-Backend

## Virtual Environment

HIGH recommend to use venv to isolate your environment.

```bash
$ python3.9 -m venv venv
$ source venv/bin/activate
```

## Dependancy

```bash
$ pip install -r requirements.txt
```

## Export Key to Environment Variables

* If using Gmail and activating the 2FA, `MAIL_PASSWORD` must be the application password.
* You may place the config file or ShellScript in the `instance` directory.
  * The `instance` directory must be located in the `flask_tutorial` directory. (See Directory Tree Below)

```bash
# export_key.sh

# JWT_SECRET_KEY: Key used for encrypting and decrypting JSON Web Tokens.
export JWT_SECRET_KEY=''

# SECRET_KEY: Application's secret key used to secure various security features in Flask.
export SECRET_KEY=''

# MAIL_DEFAULT_SENDER: Email address of the default sender for outgoing emails.
export MAIL_DEFAULT_SENDER=''

# MAIL_USERNAME: Username used for email sending.
export MAIL_USERNAME=''

# MAIL_PASSWORD: Password used for email sending. If using Gmail and activating the 2FA, `MAIL_PASSWORD` must be the application password.
export MAIL_PASSWORD=''

# SECURITY_PASSWORD_SALT: Salt value used for encrypting passwords.
export SECURITY_PASSWORD_SALT=''
```

## Add SQLite3
```bash
# ./flask_tutorial/
$ mkdir instance
$ cd instance
$ touch data.sqlite
```

## Initialize database

```bash
# ./flask_tutorial/
$ flask --app flaskr init-db
```

## How to Activate Backend

```bash
# ./flask_tutorial/
$ flask --app flaskr run --debug --port 8080
```

## Directory Tree in flask_tutorial
```
.
├── flaskr
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   ├── __init__.cpython-39.pyc
│   │   ├── auth.cpython-39.pyc
│   │   ├── db.cpython-39.pyc
│   │   └── utils.cpython-39.pyc
│   ├── api
│   │   ├── __pycache__
│   │   │   ├── arxiv.cpython-39.pyc
│   │   │   ├── top_universities.cpython-39.pyc
│   │   │   └── user_setting.cpython-39.pyc
│   │   ├── arxiv.py
│   │   ├── top_universities.py
│   │   └── user_setting.py
│   ├── auth.py
│   ├── blog.py
│   ├── db.py
│   ├── generate_table
│   │   ├── Arxiv
│   │   │   ├── arxiv_field.csv
│   │   │   ├── arxiv_id_name.csv
│   │   │   └── main.py
│   │   └── Top_University
│   │       ├── DB_Data
│   │       │   ├── academic_reputation.csv
│   │       │   ├── employer_reputation.csv
│   │       │   ├── overall.csv
│   │       │   └── university.csv
│   │       └── main.py
│   ├── models
│   │   ├── Arxiv
│   │   │   ├── __pycache__
│   │   │   │   ├── field.cpython-39.pyc
│   │   │   │   └── id_name.cpython-39.pyc
│   │   │   ├── field.py
│   │   │   └── id_name.py
│   │   ├── TopUni
│   │   │   ├── __pycache__
│   │   │   │   ├── academic_reputation.cpython-39.pyc
│   │   │   │   ├── employer_reputation.cpython-39.pyc
│   │   │   │   ├── overall.cpython-39.pyc
│   │   │   │   └── university_id_name.cpython-39.pyc
│   │   │   ├── academic_reputation.py
│   │   │   ├── employer_reputation.py
│   │   │   ├── overall.py
│   │   │   └── university_id_name.py
│   │   ├── __pycache__
│   │   │   ├── post.cpython-39.pyc
│   │   │   └── user.cpython-39.pyc
│   │   ├── post.py
│   │   └── user.py
│   ├── templates
│   │   ├── accounts
│   │   │   ├── confirm_email.html
│   │   │   ├── confirm_success.html
│   │   │   ├── forget_password.html
│   │   │   └── reset_password.html
│   │   ├── auth
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── base.html
│   │   └── blog
│   │       ├── create.html
│   │       ├── index.html
│   │       └── update.html
│   └── utils.py
└── instance
    ├── data.sqlite
    └── export_keys.sh
```
