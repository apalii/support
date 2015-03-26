#!/usr/bin/python2.7

__author__ = 'apalii'

import sys
import json
import time
import urllib2
from datetime import datetime
try :
    import argparse
except ImportError:
    print 'use python2.7 or install argparse module'
    sys.exit(1)

parser = argparse.ArgumentParser(description='Account Generator v.1.00')
parser = argparse.ArgumentParser(description="Account Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
    Examples:

    1) Test customer and accounts creation :
    ./create_accounts.py -s 192.168.197.100 -e 3 -l porta-support -p b0neynem --product zzzPortaTestProduct

    2) For MR45 and lower:
    ./create_accounts.py -s 192.168.197.100 -e 3 -l porta-support -p b0neynem --mr45

    3) Test customer and accounts termination:
    ./create_accounts.py -s 192.168.197.100 -e 3 -l porta-support -p b0neynem --cleanup
  ''')

parser.add_argument("--server", "-s", type=str, required=True, dest="serv",
                    help="IP address of the web server")
parser.add_argument("--env", "-e", type=str, required=True, dest="env",
                    help="approptiate i_env")
parser.add_argument("--login", "-l", type=str, required=True, dest="login",
                    help="login from WI")
parser.add_argument("--password", "-p", type=str, required=True, dest="password",
                    help="password from WI")
parser.add_argument("--number", "-n", type=int, dest="number", default=5000,
                    help="Number of accounts. Default 5000")
parser.add_argument("--product", type=str,
                    default='zzzPortaTestProduct', dest="product",
                    help="default value is zzzPortaTestProduct", )
parser.add_argument("--debug", action='store_true',
                    help="shows a lot of additional information")
parser.add_argument("--cleanup", action='store_true', help="Cleanup")
parser.add_argument("--mr45", action='store_true', help="For MR 45 and lower")

pargs = parser.parse_args()
if pargs.debug:
    print pargs

# Part of creation
def auth_info():
    """registration
    :rtype : str
    """
    if pargs.mr45:
        url = server + '/Session/login/{"login":"' + login + '","password":"' + password + '"}'
    else:
        url = server + '/Session/login/{}/{"login":"' + login + '","password":"' + password + '"}'
    if pargs.debug:
        print 'Request : ', url
    try:
        request = urllib2.urlopen(url)
        data = json.load(request)
        sid = data['session_id'].encode('utf-8')
        sid_params = {"session_id":sid, "i_env": env}
        if pargs.debug:
            print sid_params
        return str(sid_params).replace("'", '"').replace(" ", "")
    except:
        print 'smth goes wrong - please check credentials'
        sys.exit(1)


def add_customer():
    """add_customer method"""

    params = {"customer_info":{}}
    params["customer_info"]["name"]             = "zzzPortaSIPPerfTestCustomer"
    params["customer_info"]["login"]            = "zzzPortaSIPPerfTestCustomer"
    params["customer_info"]["i_customer_type"]  = "1"
    params["customer_info"]["i_parent"]         = "0"
    params["customer_info"]["iso_4217"]         = "USD"
    params["customer_info"]["opening_balance"]  = "0.00000"
    params["customer_info"]["credit_limit"]     = "10.00000"

    url = '{}/Customer/add_customer/{}/{}'.format(server, auth, params)
    url = url.replace("'", '"').replace(" ", "")
    if pargs.debug:
        print url
    try: 
        page = urllib2.urlopen(url)
        data = json.load(page)
    except:
        print "It seems that {} already exists".format("zzzPortaSIPPerfTestCustomer")
        sys.exit(1)
    print 'Customer(i_customer : {}) was created'.format(data['i_customer'])
    return data['i_customer'].encode('utf-8')


def get_i_product(product):
    """Getting i_product of the zzzPortaTestProduct
    :rtype : str
    """
    params = {}
    params['name'] = product # possible 'BE_Product_001' or zzzPortaTestProduct
    url = '{}/Product/get_product_list/{}/{}'.format(server, auth, params)
    url = url.replace("'", '"').replace(" ", "")
    page = urllib2.urlopen(url)
    data = json.load(page)
    if pargs.debug:
        print url
        print data
    try:
        return data['product_list'][0]['i_product'].encode('utf-8')
        print "Successfully got i_product"
    except:
        print "Can't find {} product.\nExiting...".format(product)
        print "Please use --product parameter"
        sys.exit(1)


def add_account(acc_id):
    """add_account method"""

    params = {"account_info":{}}
    params["account_info"]["activation_date"]   = datetime.now().strftime("%Y-%m-%d")
    params["account_info"]["i_product"]         = i_product
    params["account_info"]["id"]                = acc_id
    params["account_info"]["i_customer"]        = i_cust
    params["account_info"]["billing_model"]     = "1"
    params["account_info"]["opening_balance"]   = "0.00000"
    params["account_info"]["credit_limit"]      = "10.00000"
    params["account_info"]["iso_4217"]          = "USD"
    params["account_info"]["h323_password"]     = "p1$ecr3t"

    url = '{}/Account/add_account/{}/{}'.format(server, auth, params)
    url = url.replace("'", '"').replace(" ", "")
    print url
    page = urllib2.urlopen(url)
    data = json.load(page)
    return data['i_account']


# Part of termination
def term_account(acc_id):
    """terminating account"""
    params = {}
    params['i_account'] = acc_id
    url = '{}/Account/terminate_account/{}/{}'.format(server, auth, params)
    url = url.replace("'", '"').replace(" ", "")
    if pargs.debug:
        print 'Terminating account {}\n{}'.format(acc_id, url)
    try:
        page = urllib2.urlopen(url)
        data = json.load(page)
        if pargs.debug:
            print 'Terminated ', data
        return True
    except:
        return False


def term_customer(c_id):
    """terminating account"""
    params = {}
    params['i_customer'] = c_id
    url = '{}/Customer/terminate_customer/{}/{}'.format(server, auth, params)
    url = url.replace("'", '"').replace(" ", "")
    if pargs.debug:
        print 'Terminating customer {}\n{}'.format(c_id, url)
    try:
        page = urllib2.urlopen(url)
        data = json.load(page)
        if pargs.debug:
            print 'Terminated ', data
        return True
    except:
        return False


if __name__ == "__main__":
    # Globals
    server    = 'https://' + pargs.serv + '/rest'
    env       = pargs.env
    login     = pargs.login
    password  = pargs.password
    PATH_TO_CONFS = '/home/porta-one/SIP_perf_test/csv/'

    if not pargs.cleanup:
        print 'Authentification, please wait...'
        auth      = auth_info()
        time.sleep(2)
        print 'Cheking {} product...'.format(pargs.product)
        i_product = get_i_product(pargs.product)
        time.sleep(2)
        print 'Customer creation, please wait...'
        i_cust    = add_customer()
        time.sleep(2)
        print 'Accounts creation, please wait...'
        acc_list = [str(999000330000 + i) for i in xrange(1, pargs.number)]
        acc_list.insert(0, '999000330000')

        with open('i_account.log', 'w') as term_file:
            term_file.write(i_cust + '\n')
            for acc in acc_list:
                term_file.write(add_account(acc) + '\n')
        print 'i_account.log created. Now cleanup is possible.'

        with open(PATH_TO_CONFS + 'users_reg.csv', 'w') as reg_file:
            for acc in acc_list:
                line = 'sipp;1;{a};[authentication username={a} password=p1$ecr3t]'.format(a=acc)
                reg_file.write(line + '\n')
        print 'users_reg.csv created'

        with open(PATH_TO_CONFS + 'users_call.csv', 'w') as calls_file:
            while len(acc_list):
                caller, callee = acc_list.pop(), acc_list.pop()
                line = '{a};[authentication username={a} password=p1$ecr3t];{b}'.format(a=caller, b=callee)
                calls_file.write(line + '\n')
        print 'users_call.csv created'
        print 'Please perform SIP performance tests'
    else:
        to_term = []
        auth    = auth_info()
        with open('i_account.log') as term_file:
            for line in term_file:
                to_term.append(line.strip())
        print 'Accounts termination ...'
        for acc_id in to_term[1:]:
            term_account(acc_id)
        print 'Customer termination ...'
        term_customer(to_term[0])
