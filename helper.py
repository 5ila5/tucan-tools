import grades_exporter
import json
import os
import argparse
import mechanicalsoup
import getpass

GRADES_JSON = 'grades.json'
CREDENTIALS_FILE = 'user-credentials.txt'
BASE_URL = 'https://www.tucan.tu-darmstadt.de'

def get_user_credentials():
    def get_by_file():
        with open(CREDENTIALS_FILE, 'r') as f:
            contents = f.readlines()
            if len(contents) != 2:
                return None
            return {
                "username": contents[0].strip(),
                "password": contents[1].strip()
            }
    def ask_user():
        username = None
        password = None
        while username is None:
            username = input('Tucan Username: ')
        while password is None:
            password = getpass.getpass('Tucan Password: ')
        return {
            "username": username.strip(),
            "password": password.strip()
        }


    # First try to get the user credentials by file, afterwards by programm arguments
    try:
        return get_by_file()
    except:
        pass

    try:
        return ask_user()
    except:
        pass
    raise(Exception('Could not retreive username/password. Are you doing this on purpose?'))

def get_grades():
    try:
        if not os.path.exists(GRADES_JSON):
            grades = grades_exporter.get_grades()
            with open(GRADES_JSON, 'w+') as f:
                json.dump(grades, f, indent=4)
        with open(GRADES_JSON, 'r') as f:
            return json.load(f)
    except:
        raise(Exception('Could not retreive grades. grades.json is malformed or the credentials you\'ve are wrong - probably'))

def get_available_grades():
    return [1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0, 5.0]

def get_avg_from_notenspiegel_without_failed(notenspiegel):
    return get_avg_from_notenspiegel(notenspiegel[:-1])

def get_avg_from_notenspiegel(notenspiegel):
    n = [x * get_available_grades()[index] for (index, x) in enumerate(notenspiegel)]
    return sum(n) / sum(notenspiegel)

def sanitize_filename(title):
    title = title.replace(' ', '-').replace(':', '-').lower()
    return title

def get_tucan_baseurl():
    return BASE_URL

# ...
def log_into_tucan_():
    credentials = get_user_credentials()
    return log_into_tucan(credentials['username'], credentials['password'])

def log_into_tucan(username, password, browser=mechanicalsoup.Browser(soup_config={"features":"html.parser"})):
    SELECTORS = {
        "LoginUser": '#field_user',
        "LoginPass": '#field_pass',
        "LoginForm": '#cn_loginForm'
    }

    def get_redirection_link(page):
        return BASE_URL + page.soup.select('a')[2].attrs['href']

    browser = mechanicalsoup.Browser(soup_config={"features":"html.parser"})
    login_page = browser.get(BASE_URL)
    # HTML redirects, because why not
    login_page = browser.get(get_redirection_link(login_page))
    login_page = browser.get(get_redirection_link(login_page))
    login_form = login_page.soup.select(SELECTORS['LoginForm'])[0]

    login_form.select(SELECTORS['LoginUser'])[0]['value'] = username
    login_form.select(SELECTORS['LoginPass'])[0]['value'] = password

    login_page = browser.submit(login_form, login_page.url)
    redirected_url = "=".join(login_page.headers['REFRESH'].split('=')[1:])

    start_page = browser.get(BASE_URL + redirected_url)
    start_page = browser.get(get_redirection_link(start_page))
    return (browser, start_page)