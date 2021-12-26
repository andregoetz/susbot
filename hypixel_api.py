import datetime
import os
import json
import requests

path = os.path.dirname(os.path.abspath(__file__))
with open(path + '/res/config.json') as conf:
    conf = json.load(conf)


def get_player(name_or_uuid: str) -> dict:
    res = requests.get(f'https://playerdb.co/api/player/minecraft/{name_or_uuid}')
    if res.ok and (res := json.loads(res.text))['success']:
        return res['data']['player']


def get_hypixel_player(name: str) -> tuple:
    if (player := get_player(name.lower())) is not None:
        res = requests.get('https://api.hypixel.net/player', params={
            'key': conf['hypixel_api_key'],
            'uuid': player['id']
        })
        if res.ok and (res := json.loads(res.text))['success']:
            return res['player'], player['avatar']


def get_hypixel_friends(name: str) -> list:
    if (player := get_player(name.lower())) is not None:
        res = requests.get('https://api.hypixel.net/friends', params={
            'key': conf['hypixel_api_key'],
            'uuid': player['id']
        })
        if res.ok and (res := json.loads(res.text))['success']:
            return [get_player(item['uuidSender'] if (f_id := item['uuidReceiver']) == player['raw_id'] else f_id)
                    for item in res['records']]


if __name__ == '__main__':
    for i in [j['username'] for j in get_hypixel_friends('AbrahamQuintoln')]:
        print(i + ':')
        print('  Last-Login: ' + str(datetime.datetime.fromtimestamp((get_hypixel_player(i)[0]['lastLogin'] / 1000.0))))
        # print('  Friends: ' + str([k['username'] for k in get_hypixel_friends(i)]))
