#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
import datetime
import webbrowser
try:
    import urllib2
except:
    import urllib.request as urllib2
try:
    from gi.repository import Notify
except ImportError:
    sys.exit('Please install sudo apt-get install python3-gi')
try:
    import requests
except ImportError:
    sys.exit('Please install requests module')


parser = argparse.ArgumentParser(description='Ticket watcher beta',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
   $ python ticket_watcher.py -l login -p password --vk --debug
  ''')
parser.add_argument("--login", "-l", type=str, help="Login")
parser.add_argument("--password", "-p", type=str, help="Password")
parser.add_argument("--debug", action='store_true', help="Debug")
parser.add_argument("--vk", action='store_true', help="message via vk")
pargs = parser.parse_args()
if pargs.debug:
    print(pargs)


def get_tickets(login, password):
    '''Getting open tickets via RT API. Responce example:
    RT/3.8.4 200 Ok

    Found 3 tickets
    Page 1/1

    384190: Number Portability for incoming leg
    400680: [oracle lab] Restoration from backups (Lynx)
    404154: Static routing configuration on PortaSIP Switching server
    -----------------------------------------------------------------
    RT/3.8.4 200 Ok

    Found 0 tickets
    Page 1/1

    No matching results.
    '''
    rt_url = 'https://rt.portaone.com/REST/1.0/search/ticket?query='
    request = urllib2.quote("Owner='{owner}' AND Status = 'open'".format(
                                                                   owner=login))

    payload = {
        'user': login,
        'pass': password
    }

    with requests.Session() as my_session:
        if pargs.debug:
            print(rt_url + request)
        my_session.post(rt_url, data=payload)
        data = my_session.get(rt_url + request).text.split('\n\n')[2:]
        data_list = data[0].rstrip().split('\n')
    if 'No matching results.' not in data_list:
        return set(data_list)
    else:
        return set()
    '''rt_url = 'https://rt.portaone.com/REST/1.0/ticket/396939/history/'
    my_session.post(rt_url, data=payload)
    data = my_session.get(rt_url).text.split('\n\n')[2:]
    data_list = data[0].rstrip().split('\n')[-1]
    last_reply = data_list.split(':')[0]
    print last_reply
    '''


def get_weather():
    '''Getting weather forecast from yahoo
    918233 means Chernihiv
    '''
    y_url = 'https://query.yahooapis.com/v1/public/yql?q='
    baseurl = "https://query.yahooapis.com/v1/public/yql?q="
    yql_query = "select item.condition from weather.forecast where woeid=918233 and u='c'"
    yql_url = baseurl + urllib2.quote(yql_query) + "&format=json"
    data = requests.get(yql_url).json()
    if pargs.debug:
        print(yql_url)
        print(data)
    forecast = data['query']['results']['channel']['item']['condition']
    return 'Yahoo forecast : {}C  {}'.format(forecast['temp'], forecast['text'])


def vk_message(userid, message):
    '''This func sends message to appropriate user via vk.com
    '''
    token = 'ab12714294fb9e626baea03df58b7c47c4e7d401aa79e28ca6ecb9fc6eb0d7'
    vk_url = 'https://api.vk.com/method/messages.send?user_id='
    message = urllib2.quote(message)
    url = vk_url + '{}&message={}&access_token={}'.format(userid, message, token)
    if pargs.debug:
        print(url)
    response = requests.get(url).json()


def notify(mb='Ticket watcher : \n', mr='There are no tickets',
                                    mtype='dialog-information'):
    '''Appropriate notification using gi.repository
    Pynotify is deprecated.
    mb - message bold
    mr - message regular
    '''
    Notify.init("tw")
    n = Notify.Notification.new(mb, mr, mtype)
    n.show()


def notification(tickets_list):
    '''Oper some radio statios in google-chrome browser
    and every ticket in separate tab. Sends message in vk.
    '''
    vk_user_id = '17222429'
    my_radio = 'http://www.radioroks.ua/player/hardnheavy/'
    webbrowser.get('/usr/bin/google-chrome %s').open_new_tab(my_radio)
    rt_tt_link = 'https://rt.portaone.com/Ticket/Display.html?id='
    notify(mr="You have open tickets ! ! !")
    for ticket in tickets_list:
        TT_url = rt_tt_link + ticket.split(':')[0]
        webbrowser.get('/usr/bin/google-chrome %s').open_new_tab(TT_url)
    if pargs.vk:
        to_send = '\n'.join(ticket for ticket in tickets_list)
        vk_message(userid=vk_user_id, message=to_send)


def working_hours():
    '''["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    So 0 means monday etc. Hence (0,2,3) means "monday","wednesday","thursday".
    '''
    if datetime.date.today().weekday() in (0,2,3):
        return 19
    else:
        return 18


def time_left(working_hours):
    '''Shows how many hours and minutes left:
    '''
    wh = working_hours
    dt  = datetime.datetime
    now = dt.now()
    left_obj = dt(year=now.year, month=now.month, day=now.day, hour=wh) - now
    left = left_obj.__str__().split(':')[:-1]
    if pargs.debug:
        print(left_obj.__str__())
    return '{}h:{}m  left'.format(left[0], left[1])


def kurs_privat():
    '''Безналичный курс Приватбанка
    (конвертация по картам, Приват24, пополнение вкладов)
    '''
    url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=11'
    kurs = requests.get(url).json()[2]
    if pargs.debug:
        print(kurs)
    return 'PrivatBank buy {} | sale {}'.format(kurs['buy'], kurs['sale'])


class Myset(set):
    def clear(self):
        while len(self):
            self.pop()

if __name__ == "__main__":
    if not len(sys.argv) == 1:
        os.system('clear')
        print('Press ctrl+C to exit')
        watched_list = Myset()
        iteration = 0
        wh = working_hours()
        while datetime.datetime.now().time() < datetime.time(hour=wh,minute=00):
            iteration += 1
            open_tickets = get_tickets(pargs.login, pargs.password)
            if pargs.debug:
                print('iteration    : {}'.format(iteration))
                print('watched_list : {}'.format(watched_list))
                print('open_tickets : {}'.format(open_tickets))
            if iteration == 1:
                notify(mr=" started...")
                notify(mr=kurs_privat())
                notify(mb=get_weather(), mr='')
                if len(open_tickets) >= 1:
                    notify(mr="Open tickets:")
                    for ticket in open_tickets:
                        watched_list.add(ticket)
                        notify(mr=ticket)
                    time.sleep(100)
                else:
                    notify()
                    time.sleep(100)
            else:
                if len(open_tickets.difference(watched_list)) == 0:
                    notify(mb='There are no tickets !', mr='')
                    if len(open_tickets) == 0:
                        watched_list.clear()
                    if iteration % 5 == 0:
                        notify(mb=time_left(wh), mr='')
                        notify(mb=kurs_privat(), mr='')
                    print(time.ctime(time.time()) + ' no new tickets so far')
                    time.sleep(300)
                else:
                    tickets_dif = open_tickets.difference(watched_list)
                    watched_list.clear()
                    notification(tickets_dif)
                    for ticket in open_tickets:
                        watched_list.add(ticket)
                    time.sleep(300)
    else:
        print('Use --help for more detail')
