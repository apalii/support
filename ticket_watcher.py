#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import urllib2
import argparse
import datetime 
#import traceback
import webbrowser
try:
    import requests
except ImportError:
    print('Please install requests module')
    sys.exit(1)


parser = argparse.ArgumentParser(description='Ticket watcher beta',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
   $ python ticket_watcher.py -l login -p password
  ''')
parser.add_argument("--login", "-l", type=str, help="Login")
parser.add_argument("--password", "-p", type=str, help="Password")
parser.add_argument("--debug", action='store_true', help="Debug")
parser.add_argument("--vk", action='store_true', help="message via vk")
pargs = parser.parse_args()
if pargs.debug:
    print(pargs)


def get_tickets(login, password):
    '''Getting open tickets via RT API. Respond example:
    RT/3.8.4 200 Ok

    Found 1 tickets
    Page 1/1

    384190: Number Portability for incoming leg
    '''
    rt_url = 'https://rt.portaone.com/REST/1.0/search/ticket?query='
    request = urllib2.quote("Owner='{owner}' AND Status = 'open'".format(owner=login))

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
    return set(data_list)


def vk_message(userid, message):
    '''This func sends message to appropriate user via vk.com 
    '''
    token = 'decb1101f64a6624fd054f360ef223e7f43480309dc8747e3f972aebccc1544771c10934efa666e9e0e8c'
    vk_url = 'https://api.vk.com/method/messages.send?user_id='
    message = urllib2.quote(message)
    url = vk_url + '{}&message={}&access_token={}'.format(userid, message, token)
    if pargs.debug:
        print(url)
    response = requests.get(url).json()


def notification(tickets_list):
    '''Docstring 
    ticket_number = rest_response.text.split('\n\n')[1].split('\n')[0]
    '''
    my_radio = 'http://www.radioroks.ua/player/hardnheavy/'
    webbrowser.get('/usr/bin/google-chrome %s').open_new_tab(my_radio)
    os.system('notify-send "You have open tickets ! ! !"') 
    print('\nYour tickets are the following:\n')
    for ticket in tickets_list:
        print(ticket)
    if pargs.vk:
        to_send = '\n'.join(i for i in tickets_list)
        vk_message(userid='17222429', message=to_send)

def working_hours():
    '''days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    So 0 means monday etc. Hence (0,2,3) means "monday","wednesday","thursday".
    '''
    if datetime.date.today().weekday() in (0,2,3):
        return 19
    else:
        return 18


def time_left(working_hours):
    '''Shows how many hours and minutes left:
    '''
    dt  = datetime.datetime
    now = dt.now()
    left_obj = dt(year=now.year,month=now.month,day=now.day,hour=working_hours) - now
    left = left_obj.__str__().split(':')[:-1]
    return '{}h:{}m  left'.format(left[0], left[1])


if __name__ == "__main__":
    if not len(sys.argv) == 1:
        os.system('clear')
        print('Press ctrl+C to exit')
        watched_list = set()
        iteration = 0
        wh = working_hours()
        while datetime.datetime.now().time() < datetime.time(hour=wh, minute=00):
            iteration += 1
            open_tickets = get_tickets(pargs.login, pargs.password)
            if pargs.debug:
                print('iteration    : {}'.format(iteration))
                print('watched_list : {}'.format(watched_list))
                print('open_tickets : {}'.format(open_tickets))
            if iteration == 1:
                os.system('notify-send "Ticket watcher started..."')
                if len(open_tickets) >= 1:
                    os.system('notify-send "Open tickets:"')
                    for ticket in open_tickets:
                        watched_list.add(ticket)
                        os.system('notify-send "{}"'.format(ticket))
                    time.sleep(300)
                else:
                    os.system('notify-send "There are no tickets !"')
                    time.sleep(300)
            else:
                if len(open_tickets.difference(watched_list)) == 0:
                    os.system('notify-send "No new tickets"')
                    os.system('notify-send "{}"'.format(time_left(wh)))
                    print(time.ctime(time.time()) + ' no new tickets so far')
                    time.sleep(300)
                else:
                    tickets_dif = open_tickets.difference(watched_list)
                    notification(tickets_dif)
                    for ticket in tickets_dif:
                        watched_list.add(ticket)
                    time.sleep(300)
    else:
        print('Use --help for more detail')
