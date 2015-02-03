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
   $ python timezone.py -l login -p password
  ''')
parser.add_argument("--login", "-l", type=str, help="Login")
parser.add_argument("--password", "-p", type=str, help="Password")
parser.add_argument("--debug", action='store_true', help="Debug")
parser.add_argument("--vk", action='store_true', help="message via vk")
pargs = parser.parse_args()
if pargs.debug:
    print(pargs)


def get_tickets(login, password):
    '''Getting open tickets via RT API 
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
        data = my_session.get(rt_url + request)
    return data


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


if __name__ == "__main__":
    #ticket_number = rest_response.text.split('\n\n')[1].split('\n')[0]
    if not len(sys.argv) == 1:
        os.system('clear')
        print('Press ctrl+C to exit')
        watched_list = set()
        iteration = 0
        while datetime.datetime.now().time() < datetime.time(hour=18, minute=00):
            iteration += 1
            rest_response = get_tickets(pargs.login, pargs.password)
            open_tickets = rest_response.text.split('\n\n')[2:]
            if iteration == 1:
                os.system('notify-send "Ticket watcher started..."')
                if len(open_tickets) >= 1 and 'No matching results.' \
                                            not in open_tickets[0]: 
                    for ticket in open_tickets:
                        watched_list.add(ticket)
                        os.system('notify-send "Open tickets:"')
                        os.system('notify-send "{}"'.format(ticket))
                    time.sleep(300)
                else:
                    os.system('notify-send "There are no tickets !"')
                    os.system('notify-send "You are lucky (: "')
                    time.sleep(300)
            else:
                if len(open_tickets) == len(watched_list) or len(watched_list) == 0:
                    os.system('notify-send "No new tickets"')
                    print(time.ctime(time.time()) + ' no new tickets so far')
                    time.sleep(300)
                else:
                    notification(open_tickets)
                    for ticket in open_tickets:
                        watched_list.add(ticket)
                    time.sleep(20)
    else:
        print('Use --help for more detail')

