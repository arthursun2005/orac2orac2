import requests
import time
import random
import string
from bs4 import BeautifulSoup

base1 = 'https://orac.amt.edu.au/'

headers = {
    # go to orac1, log in, inspect element, go to request headers, and then copy the cookie string in
    'Cookie': 'aioc_submission_train=aioc; aioc_training_username=xxx; aioc_training_password=xxx'
}

h2 = {
    # same deal for orac2
    'Cookie': 'csrftoken=xxx; sessionid=xxx'
}

with requests.get(f'{base1}/cgi-bin/train/hub.pl?expand=all', headers=headers) as res:
    u = str(res.content)

solved = []

def get_code(url):
    with requests.get(f'{base1}/{url}', headers=headers) as res:
        u = str(res.content)
    a = u.find('alert-success')
    u = u[a + 1:]
    a = u.find('href')
    b = u[a:].find('>') + a
    url = u[a + 6:b - 1]
    with requests.get(f'{base1}/{url}', headers=headers) as res:
        soup = BeautifulSoup(res.content, 'html.parser')
    for lb in soup.findAll('br'): lb.replaceWith('###')
    code = soup.find(class_='prettyprint').text
    return code.replace('###', '\n')

# dissecting html
idx = u.find('alert-success')
while idx != -1:
    u = u[idx + 1:]
    a = u.find('problemid')
    if u.find('class') < a:
        idx = u.find('alert-success')
        continue
    a = u[a:].find('>') + a
    b = u.find('/a')
    name = u[a + 1:b - 1]
    a = u.find('href')
    b = u[a:].find('>') + a
    url = u[a + 6:b - 1]
    if len(name) >= 1:
        solved.append((name, url))
    idx = u.find('alert-success')

solved = list(set(solved))

with requests.get('https://orac2.info/hub/personal/', headers=h2) as res:
    u = str(res.content)

cnt = 0

todo = []

b2 = 'https://orac2.info'

for name, url in solved:
    k = u.find(f'>{name}<')
    if k == -1: continue
    k2 = u[:k].rfind('class')
    k3 = u[:k].rfind('href')
    u2 = u[k3+6:k-1]
    p = u[k2:k].find('solved') != -1
    if not p:
        cnt += 1
        todo.append((name, p, url, u2))
        print(k, name, u2, p, sep='|')

print(f'Pot: {cnt}')
# exit(0)

def getmt(url):
    with requests.get(f'{b2}{url}submissions', headers=h2) as res:
        u = str(res.text)
    a = u.find('csrfmiddlewaretoken')
    return u[a + 28:a + 92]

def submit(url, code):
    p = {
            # 'csrfmiddlewaretoken': ''.join(random.choices(string.ascii_letters + string.digits, k=64)),
            'csrfmiddlewaretoken': getmt(url),
            'language': 'CPP11',
            'source_code': code,
    }

    with requests.post(f'{b2}{url}submit', data=p, headers=h2) as res:
        pass

for name, p, url, u2 in todo:
    try:
        submit(u2, get_code(url))
        print(f'{name}... OK', flush=True)
    except:
        print(f'{name}... ERROR', flush=True)
    time.sleep(3)
