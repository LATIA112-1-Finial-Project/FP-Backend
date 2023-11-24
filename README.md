# FP-Backend
## Virtual Environment

HIGH recommend to use venv to isolate your environment.

```bash
$ python3.9 -m venv venv
$ source venv/bin/activate
```

## Dependancy

* Requirements.txt
  * ```bash
    $ pip install -r requirements.txt
    ```

## How To Use

* ```bash
    $ cd app
    $ python app.py
    ```
* Then open any api connect test tool
  *  `GET` Method and `http://127.0.0.1:8080/api/v1/user/test/` can use the testing api, and get a 200 response of JSON List.


## Initialize database

```bash
$ flask --app flaskr init-db
```