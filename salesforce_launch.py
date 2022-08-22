#!/usr/bin/env python3
# encoding: utf-8

from workflow import Workflow, PasswordNotFound
from workflow.notify import notify
from workflow.web import get
import sys
import salesforce_api
import subprocess
import os



def main(wf):

    # Get query from Alfred
    if len(wf.args):
        query = wf.args[0]
    else:
        query = ''

    # Splitting query
    query = query.split()
    if len(query) > 0:
        query_0 = query[0]
    else:
        query_0 = None
    if len(query) > 1:
        query_1 = query[1]
    else:
        query_1 = None

    # Trying to get access_token
    try:
        access_token = wf.get_password('access_token')
    except PasswordNotFound:
        access_token = None

    if query_0 == 'login':

        notify('Salesforce', 'Please connect to your Salesforce account')
        wf.logger.info("Launch: nohup python3 ./server.py")
        subprocess.Popen(['nohup', 'python3', './server.py'])
        url = salesforce_api.get_oauth_url()
        wf.logger.info("Open: %s" % url)
        subprocess.call(['open', url])

    elif query_0 == 'logout':

        wf.delete_password('instance_url')
        wf.delete_password('refresh_token')
        wf.delete_password('access_token')
        
        notify('Salesforce', 'You are logged out')

    elif query_0 == 'debug':

        wf.logger.info(wf.settings)
        wf.logger.info(os.path.dirname(os.path.abspath(__file__)))
        wf.logger.info(get("https://www.howsmyssl.com/a/check").text)
        notify("Opening of the folder that contains debug logs")
        wf.open_cachedir()

    elif query_0 == 'switch':

        use_classic = wf.settings.get("use_classic", False)
        

        if use_classic == True:
            wf.settings["use_classic"] = False
            wf.settings.save()
            notify('Salesforce', 'Links will open in the Lightning interface')
        else:
            wf.settings["use_classic"] = True
            wf.settings.save()
            notify('Salesforce', 'Links will open in the Classic interface')


    elif query_0.startswith('http'):

        subprocess.call(['open', query_0])

    else:

        notify('Else', 'My Text')


if __name__ == "__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
