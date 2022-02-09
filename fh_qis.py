import json
import requests
from bs4 import BeautifulSoup

session = requests.Session()


def login():
    with open('res/config.json', 'r') as conf:
        conf = json.load(conf)
    url = 'https://www.qis.fh-aachen.de/qisserver/rds?state=user&type=1&category=auth.login&startpage=portal.vm&breadCrumbSource=portal'
    data = {
        'asdf': conf['fh_username'],
        'fdsa': conf['fh_password'],
        'submit': 'Login Prüfungsanmeldung/Notenspiegel '
    }
    res = session.post(url, data)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup.find('a', text='Notenspiegel').get('href').split('asi=')[1]


def notenspiegel(asi):
    url = 'https://www.qis.fh-aachen.de/qisserver/rds?state=info&application=qispos&moduleParameter=prfAnmStudent&next=info.vm&state2=prfAnmStudent&next2=tree.vm&nextdir=qispos/prfAnm/student&asi='
    data = {
        'checkbox': 'y',
        'cont': 'Weiter'
    }
    res = session.post(url + asi, data)
    soup = BeautifulSoup(res.text, 'html.parser')
    url = soup.find('a', {'class': 'Konto'}).get('href')
    res = session.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    url = soup.find_all('a', {'class': 'Konto'})[2].get('href')
    res = session.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    url = soup.find_all('a', {'class': 'Konto'})[3].get('href')
    res = session.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    imgs = soup.find('li', {'class': 'treelist'}).find_all('img')[4:-1]
    noten = {}
    for img in imgs:
        content = img.get('alt').strip().split('[')
        fach = ' '.join(content[0].split(' ')[2:]).strip()
        note = content[1].split('Note: ')[1].split(';')[0] if len(content) == 2 else None
        noten[fach] = note
    return noten


def check_for_changes():
    print('Checking...')
    with open('res/noten.json', 'r') as alte_noten:
        alte_noten = json.load(alte_noten)
    neue_noten = notenspiegel(login())
    changes = {}
    if neue_noten != alte_noten:
        with open('res/noten.json', 'w') as file:
            json.dump(neue_noten, file, indent=2)
        for fach in alte_noten:
            if alte_noten[fach] != neue_noten[fach]:
                changes[fach] = neue_noten[fach]
    return changes


if __name__ == '__main__':
    result = check_for_changes()
    for key in result:
        print(key + ': ' + result[key])
