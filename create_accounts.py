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
"""
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
"""
parser.add_argument("--debug", action='store_true',
                    help="shows a lot of additional information")
parser.add_argument("--cleanup", action='store_true', help="Cleanup")
parser.add_argument("--mr45", action='store_true', help="For MR 45 and lower")

class MyArgs(object):
    '''This simple class just imitates an argsparse
       module so that I can avoid a huge refactoring of the whole script.
       Just namespace.
    '''

    def __init__(self, **entries): 
        self.__dict__.update(entries)  


    def debug(self):
        print("Parameters are the following :")
        for key, value in self.__dict__.items():
            print("key : {:<15} value : {:<10}  {}".format(key, value, type(value)))

            
def conf_reader():
    '''This simple function reads the config and 
       returns a dict with parameters for a class
    ''' 
    config = '/home/apalii/Desktop/GIT/support/sipperftest.conf'
    params = {}
    pre_list = []
    valid = ('server', 'login', 'password', 
             'environment', 'product', 'mr45', 
             'number_of_accounts',
             'customer_name', 'first_account_number',
             'account_password', 'currency')
    if os.path.isfile(config):
        with open(config) as conf:
            for param in conf:
                if not param.startswith('#') and not len(param.rstrip()) == 0:
                    try:
                        key = param.rstrip().split('=')[0]
                        value = param.rstrip().split('=')[1]
                    except:
                        print "Incorrect format : {}".format(param)
                        sys.exit(1)
                    if key not in valid:
                        print "Unknown parameter : '{}'  skipped.".format(key)
                    else: 
                        params[key] = value
                else:
                    continue
        # Checking MR version 
        mr_grep = "rpm -q --queryformat '%{VERSION}' porta-common"
        mr_str = subprocess.Popen(mr_grep, shell=True, stdout=subprocess.PIPE).stdout.read().rstrip()
        # Expected value: 40.3
        mr = int(mr_str.split('.')[0])
        params[mr45] = True if mr >= 45 else False
    else:
        print 'Error : there is no {} file !'.format(config)
        sys.exit(1)
    if not len(valid) == len(params):
        print "Some parameter is missing or extra exists.\nPlease check conf file"
        print valid
        sys.exit(1)

    return params

# Creating of pargs instance as it was before 
# Parameters from config file
dict_with_params = conf_reader()
pargs = MyArgs(**dict_with_params)

# Parameters from the command line (pargs changed to pargs2)
pargs2 = parser.parse_args()
if pargs2.debug:
    print pargs
    pargs.debug()

# ------------------------------------------------
# Part of creation
def auth_info():
    """registration
    :rtype : str
    """
    if pargs.mr45:
        url = server + '/Session/login/{"login":"' + login + '","password":"' + password + '"}'
    else:
        url = server + '/Session/login/{}/{"login":"' + login + '","password":"' + password + '"}'
    if pargs2.debug:
        print 'Request : ', url
    try:
        request = urllib2.urlopen(url)
        data = json.load(request)
        sid = data['session_id'].encode('utf-8')
        sid_params = {"session_id":sid, "i_env": env}
        if pargs2.debug:
            print sid_params
        return str(sid_params).replace("'", '"').replace(" ", "")
    except:
        print 'smth goes wrong - please check credentials'
        sys.exit(1)


def add_customer(cust_name, currency):
    """add_customer method"""

    params = {"customer_info":{}}
    params["customer_info"]["name"]             = cust_name
    params["customer_info"]["login"]            = "cust_name"
    params["customer_info"]["i_customer_type"]  = "1"
    params["customer_info"]["i_parent"]         = "0"
    params["customer_info"]["iso_4217"]         = currency
    params["customer_info"]["opening_balance"]  = "0.00000"
    params["customer_info"]["credit_limit"]     = "10.00000"

    url = '{}/Customer/add_customer/{}/{}'.format(server, auth, params)
    url = url.replace("'", '"').replace(" ", "")
    if pargs2.debug:
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
    if pargs2.debug:
        print url
        print data
    try:
        return data['product_list'][0]['i_product'].encode('utf-8')
        print "Successfully got i_product"
    except:
        print "Can't find {} product.\nExiting...".format(product)
        print "Please use --product parameter"
        sys.exit(1)


def add_account(acc_id, currency, password):
    """add_account method"""

    params = {"account_info":{}}
    params["account_info"]["activation_date"]   = datetime.now().strftime("%Y-%m-%d")
    params["account_info"]["i_product"]         = i_product
    params["account_info"]["id"]                = acc_id
    params["account_info"]["i_customer"]        = i_cust
    params["account_info"]["billing_model"]     = "1"
    params["account_info"]["opening_balance"]   = "0.00000"
    params["account_info"]["credit_limit"]      = "10.00000"
    params["account_info"]["iso_4217"]          = currency
    params["account_info"]["h323_password"]     = password

    url = '{}/Account/add_account/{}/{}'.format(server, auth, params)
    url = url.replace("'", '"').replace(" ", "")
    print url
    page = urllib2.urlopen(url)
    data = json.load(page)
    return data['i_account']

# ------------------------------------------------
# Part of termination
# term_account is excess, will be removed
def term_account(acc_id):
    """terminating account"""
    params = {}
    params['i_account'] = acc_id
    url = '{}/Account/terminate_account/{}/{}'.format(server, auth, params)
    url = url.replace("'", '"').replace(" ", "")
    if pargs2.debug:
        print 'Terminating account {}\n{}'.format(acc_id, url)
    try:
        page = urllib2.urlopen(url)
        data = json.load(page)
        if pargs2.debug:
            print 'Terminated ', data
        return True
    except:
        return False


def term_customer(c_id):
    """terminating customer"""
    params = {}
    params['i_customer'] = c_id
    url = '{}/Customer/terminate_customer/{}/{}'.format(server, auth, params)
    url = url.replace("'", '"').replace(" ", "")
    if pargs2.debug:
        print 'Terminating customer {}\n{}'.format(c_id, url)
    try:
        page = urllib2.urlopen(url)
        data = json.load(page)
        if pargs2.debug:
            print 'Terminated ', data
        return True
    except:
        return False


if __name__ == "__main__":
    # Globals
    server    = 'https://' + pargs.serv + '/rest'
    env       = pargs.environment
    login     = pargs.login
    password  = pargs.password
    PATH_TO_CONFS = '/home/porta-one/SIP_perf_test/csv/'
    PATH_TO_LOG   = '/porta_var/temp/i_customer.log'

    if not pargs2.cleanup:
        print 'Authentification, please wait...'
        auth      = auth_info()
        time.sleep(2)
        print 'Cheking {} product...'.format(pargs.product)
        i_product = get_i_product(pargs.product)
        time.sleep(2)
        print 'Customer creation, please wait...'
        i_cust    = add_customer(pargs.customer_name, pargs.currency)
        time.sleep(2)

        print 'Accounts creation, please wait...'
        acc_list = [str(999000330000 + i) for i in xrange(1, pargs.number_of_accounts)]
        acc_list.insert(0, '999000330000')
        for acc in acc_list:
            add_account(acc, pargs.currency, pargs.account_password)


        with open(PATH_TO_LOG, 'w') as term_file:
            term_file.write('Do not remove this file'+ '\n')
            term_file.write(i_cust + '\n')
        print 'i_account.log created. Now cleanup is possible.'

        with open(PATH_TO_CONFS + 'users_reg.csv', 'w') as reg_file:
            reg_file.write('SEQUENTIAL' + '\n') 
            for acc in acc_list:
                line = 'sipp;1;{a};[authentication username={a} password=p1$ecr3t]'.format(a=acc)
                reg_file.write(line + '\n')
        print 'users_reg.csv created'

        with open(PATH_TO_CONFS + 'users_call.csv', 'w') as calls_file:
            calls_file.write('SEQUENTIAL' + '\n')
            while len(acc_list):
                caller, callee = acc_list.pop(), acc_list.pop()
                line = '{a};[authentication username={a} password=p1$ecr3t];{b}'.format(a=caller, b=callee)
                calls_file.write(line + '\n')
        print 'users_call.csv created'
        print 'Please perform SIP performance tests'
    else:
        to_term = []
        auth    = auth_info()
        with open(PATH_TO_LOG) as term_file:
            for line in term_file:
                to_term.append(line.strip())
        print 'Customer termination ...'
        term_customer(to_term[1])
