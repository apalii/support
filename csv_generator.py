#!/usr/bin/python2.7

__author__ = 'apalii'

from create_accounts import MyArgs
import sys

def conf_reader():
    '''This simple function reads the config and 
       returns a dict with parameters for a class
    ''' 
    config = '/home/porta-one/SIP_perf_test/etc/sipperftest.conf'
    params = {}
    pre_list = []
    valid = ('server', 'login', 'password', 
             'environment', 'product',
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
        # All paremeter should be equeal to len of "valid" list 
        if not len(valid) == len(params) - 1:
            print "Some parameter is missing or extra exists.\nPlease check conf file"
            print valid
            print params
            sys.exit(1)
        if int(params['number_of_accounts']) % 2 != 0:
            print "Number of accounts should be even number"
            print "Recheck number_of_accounts parameter in config file"
            sys.exit(1)
    else:
        print 'Error : there is no {} file !'.format(config)
        sys.exit(1)
    return params

# Creating of pargs instance as it was before 
# Parameters from config file
dict_with_params = conf_reader()
pargs = MyArgs(**dict_with_params)


if __name__ == "__main__":
    # Globals
    PATH_TO_CONFS = '/home/porta-one/SIP_perf_test/csv/'

    acc_list = [pargs.first_account_number + i) for i in xrange(1, int(pargs.number_of_accounts))]
    acc_list.insert(0, pargs.first_account_number)

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
