import requests
requests.packages.urllib3.disable_warnings() 

import time
import smtplib
import logging


from bs4 import BeautifulSoup

from hosts import hosts


###############################################################################################
# This script will force automatic synchronization the Palo Alto High Availability.
# It needs the hosts.py file to use as a template and automatically identifies who the master is between the two.
# A user has the same access token as long as it is the same name in every PA.
# When finished executing, a script with name of "ha.log" is generated.
###############################################################################################


logging.basicConfig(level=logging.INFO, filename="ha.log", format='[ %(asctime)s ] %(levelname)s - %(message)s')

for host in hosts:
    try:
        logging.info("Starting synchronization on: \n\
                                    HOST: %s \n\
                                    IP: %s \n\
                                    COUNTRY: %s" %(host['host'], 
                                    host['ip'], 
                                    host['country'])
                    )


        token = 'token' # your token here
        ip_firewall = host['ip']
        url = "https://%s/api/?type=op&cmd=<show><high-availability><state></state></high-availability></show>&key=%s" %(ip_firewall, token)

        req = requests.get(url, verify=False)
        
        if req.status_code == 403:
            logging.error('Invalid token\n \
=========================================================================')
            continue

        
        res = req._content
        sync = BeautifulSoup(res, 'xml').find_all('running-sync')[-1].text

        if sync == 'synchronized':
            logging.info('%s synchronized\n \
=========================================================================' %host['host'])
            continue
        if sync == 'synchronization in progress':
            logging.info('%s synchronization is already in progress.\n \
=========================================================================' %host['host'])
            continue
        else:
            state = BeautifulSoup(res, 'xml').find_all('state')[-1].text

            if state == 'active':
                ip_active = BeautifulSoup(res, 'xml').find_all('ha1-backup-ipaddr')[-1].text
                ip_passive = ip_firewall
            else:
                ip_active = ip_firewall
                ip_passive = BeautifulSoup(res, 'xml').find_all('ha1-backup-ipaddr')[0].text

            logging.info('Firewall active identified: %s' %ip_active)
            logging.info('Forcing synchronization')

            command_sync = "https://%s/api/?type=op&cmd=<request><high-availability><sync-to-remote><running-config></running-config></sync-to-remote></high-availability></request>&key=%s" %(ip_active, token)
            
            req = requests.get(command_sync, verify=False)._content

            
            res = BeautifulSoup(req, 'xml').find_all('line')[-1].text

            print (res)
            
            if res == 'Local commit jobs are queued. running configuration will not be synchronized with HA peer':
                logging.error('There is a commit running at this time, it is not possible to synchronize.')
                continue
                
            elif res == 'Other administrators are holding commit locks.':
                logging.info('There is active commit lock')
                logging.info('Removing commit lock')

                show_commit = "https://%s/api/?type=op&cmd=<show><commit-locks></commit-locks></show>&key=%s" %(ip_passive, token)
                req = requests.get(show_commit, verify=False)._content

                res = BeautifulSoup(req, 'xml').find_all('entry')
                
                for user in res:
                    remove_commit = "https://%s/api/?type=op&cmd=<request><commit-lock><remove><admin>%s</admin></remove></commit-lock></request>&key=%s" %(ip_passive, user['name'], token)
                    req = requests.get(remove_commit, verify=False)._content
                    logging.info("%s's commit lock removed" %user['name'])

                logging.info('Forcing synchronization again')

                command_sync = "https://%s/api/?type=op&cmd=<request><high-availability><sync-to-remote><running-config></running-config></sync-to-remote></high-availability></request>&key=%s" %(ip_active, token)

                req = requests.get(command_sync, verify=False)._content
                
                res = BeautifulSoup(req, 'xml').find_all('line')[-1].text

                if res != 'HA synchronization job has been queued on peer. \
                        Please check job status on peer.' \
                or res != 'HA synchronization is already in progress. \
                        running configuration will not be synchronized with HA peer':
                    print('envia email')
                    logging.error('Sync error, sending email to email@domain.com.br\n \
=========================================================================')
                else:
                    logging.info('Synchronization DONE \n \
=========================================================================')

            elif res != 'HA synchronization job has been queued on peer. \
                        Please check job status on peer.' \
            or res != 'HA synchronization is already in progress. \
                        running configuration will not be synchronized with HA peer':
                logging.error('Sync error, sending email to email@domain.com.br\n \
=========================================================================')            
            else:
                logging.info('Synchronization DONE \n \
=========================================================================')
                # server = smtplib.SMTP('host', 25)

                
                # Send the mail
                # msg = "Problema de sync em %s " %host
                # server.sendmail("from", "to", msg)
    except Exception as e:
        logging.error("%s \n \
=========================================================================" %e)   
