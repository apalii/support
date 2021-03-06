#!/usr/bin/python2.7

__author__ = 'apalii'

import os
import re
import sys
import json
import time
import urllib2
from datetime import datetime
from lib.args import MyArgs
try:
    import argparse
except ImportError:
    sys.exit('use python2.7 or install argparse module')

# root-level privileges check
if os.geteuid() != 0:
    sys.exit("You need to have root privileges to run this script")

parser = argparse.ArgumentParser(description='Account Generator v.3')
parser.add_argument("--debug", action='store_true',
                    help="shows a lot of additional information")
parser.add_argument("--cleanup", action='store_true',
                    help="Terminates customer")


def conf_reader():
    '''This simple function reads the config and
       returns a dict with parameters
    '''
    config = os.getcwd() + '/etc/gen_accounts.conf'
    params = {}
    pre_list = []
    valid = ('server', 'login', 'password',
             'environment', 'product',
             'number_of_accounts',
             'customer_name', 'first_account_number',
             'account_password',)
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
        mr_pattern = re.compile(r'MR(\d+)\.\d{1}')
        mr = re.findall(mr_pattern, os.environ['PS1'])[0]
        params['mr45'] = True if int(mr) >= 45 else False
    else:
        print 'Error : there is no {} file !'.format(config)
        sys.exit(1)
    if not len(valid) == len(params) - 1:
        print "Some parameter is missing or extra exists.\nPlease check conf file"
        print valid
        print params
        sys.exit(1)
    if int(params['number_of_accounts']) % 2 != 0:
        print "Number of accounts should be even number"
        print "Recheck number_of_accounts parameter in the config file"
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
    """registration :rtype : str"""

    params = {}
    params['password'] = password
    if pargs.login == 'soap-root':
        params['user'] = 'soap-root'
    else:
        params['login'] = pargs.login
    if pargs.mr45:
        url = server + '/Session/login/{}/' + '{}'.format(params)
    else:
        url = server + '/Session/login/{}'.format(params)
    url = url.replace("'", '"').replace(" ", "")
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
    login = cust_name + '_' + str(time.time()).split('.')[0]
    rtpp_always = {"flag_value":"3","name":"rtpp_level"}
    params = {"customer_info":{}}
    params["customer_info"]["name"]             = cust_name
    params["customer_info"]["login"]            = login
    params["customer_info"]["i_customer_type"]  = "1"
    params["customer_info"]["i_parent"]         = "0"
    params["customer_info"]["iso_4217"]         = currency
    params["customer_info"]["opening_balance"]  = "0.00000"
    params["customer_info"]["credit_limit"]     = "10.00000"
    params["customer_info"]["service_features"] = [rtpp_always]

    url = '{}/Customer/add_customer/{}/{}'.format(server,
                                                  auth,
                                                  params)
    url = url.replace("'", '"').replace(" ", "")
    if pargs2.debug:
        print url
    try:
        page = urllib2.urlopen(url)
        data = json.load(page)
    except:
        print "It seems that {} already exists".format(cust_name)
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
        i_prod = data['product_list'][0]['i_product'].encode('utf-8')
        pargs.currency = data['product_list'][0]['iso_4217'].encode('utf-8')
        print "\nSuccessfully got i_product {} and currency {}\n".format(i_prod,
            pargs.currency)
        return i_prod
    except:
        print "Can't find {} product.\nExiting...".format(product)
        print "Please correct 'product' parameter"
        sys.exit(1)


def gen_accounts(start_id, number, currency):
    '''Account generator method'''

    params = {}
    params['batch']             = "sipperftest" + str(int(time.time()))
    params['gen_method']        = 'S'
    params['gen_start_id']      = start_id # First acc number
    params['gen_amount']        = number
    params["activation_date"]   = datetime.now().strftime("%Y-%m-%d")
    params["i_product"]         = i_product
    params["i_customer"]        = i_cust
    params["billing_model"]     = "-1"
    params["opening_balance"]   = "3.00000"
    #params["credit_limit"]     = "10.00000"
    params["iso_4217"]          = currency
    params["gen_h323_method"]   = "empty"
    params["inactive"]          = "N"

    url = '{}/Account/generate_accounts/{}/{}'.format(server,
                                                      auth,
                                                      params)
    url = url.replace("'", '"').replace(" ", "")
    if pargs2.debug:
        print url
    try:
        page = urllib2.urlopen(url)
        data = json.load(page)
    except:
        sys.exit('please check gen_accounts method')
    print "Generation result - {}".format(data)

# ------------------------------------------------
# Part of termination

def term_customer(c_id):
    """terminating customer"""
    params = {}
    params['i_customer'] = c_id
    url = '{}/Customer/terminate_customer/{}/{}'.format(server,
                                                        auth,
                                                        params)
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
    server    = 'https://' + pargs.server + '/rest'
    env       = pargs.environment
    login     = pargs.login
    password  = pargs.password
    PATH_TO_CONFS = os.getcwd() +  '/csv/'
    PATH_TO_LOG   = os.getcwd() + '/tmp/i_customer.log'

    if not pargs2.cleanup:
        print 'Authentification, please wait...\n'
        auth      = auth_info()
        time.sleep(2)
        print 'Cheking {} product...\n'.format(pargs.product)
        i_product = get_i_product(pargs.product)
        time.sleep(2)
        print 'Customer creation, please wait...\n'
        i_cust    = add_customer(pargs.customer_name, pargs.currency)
        time.sleep(2)
        with open(PATH_TO_LOG, 'w') as term_file:
            term_file.write('Do not remove this file'+ '\n')
            term_file.write(i_cust + '\n')
        print 'i_customer.log created. Now --cleanup is possible.'

        print 'Accounts creation, please wait...'
        acc_list = [str(int(pargs.first_account_number) + i)
                    for i in xrange(1, int(pargs.number_of_accounts))]
        acc_list.insert(0, pargs.first_account_number)
        # Should we use account generator or not
        if pargs.mr45:
            gen_accounts(pargs.first_account_number, pargs.number_of_accounts,
                         pargs.currency)
        else:
            print "There is no generate_account API method in current MR"
            sys.exit("Use csv_generator.py instead.")

        with open(PATH_TO_CONFS + 'users_reg.csv', 'w') as reg_file:
            reg_file.write('SEQUENTIAL' + '\n')
            for acc in acc_list:
                line = 'sipp;1;{a};[authentication username={a} password={b}]'.format(
                    a=acc,
                    b=pargs.account_password)
                reg_file.write(line + '\n')
        print 'users_reg.csv created'

        with open(PATH_TO_CONFS + 'users_call.csv', 'w') as calls_file:
            calls_file.write('SEQUENTIAL' + '\n')
            while len(acc_list):
                caller, callee = acc_list.pop(), acc_list.pop()
                line = '{a};[authentication username={a} password={b}];{c}'.format(
                    a=caller,
                    b=pargs.account_password
                    c=callee)
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
