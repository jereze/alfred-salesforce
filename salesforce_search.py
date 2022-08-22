#!/usr/bin/env python3
# encoding: utf-8

from workflow import Workflow, ICON_ERROR, ICON_ACCOUNT, ICON_SWITCH, ICON_INFO, PasswordNotFound
import sys
import salesforce_api



SETTINGS = [
    {
        'title': 'Login',
        'autocomplete': '> Login',
        'arg': 'login',
        'icon': ICON_ACCOUNT
    },
    {
        'title': 'Logout',
        'autocomplete': '> Logout',
        'arg': 'logout',
        'icon': ICON_SWITCH
    },
    {
        'title': 'Debug',
        'autocomplete': '> Debug',
        'arg': 'debug',
        'icon': ICON_SWITCH
    },
    {
        'title': 'Switch opening results in Classic/Lightning',
        'autocomplete': '> Switch opening results in Classic/Lightning',
        'arg': 'switch',
        'icon': ICON_SWITCH
    }
]

SEARCH = [
    {
        'keyword': None
    },
    {
        'keyword': 'oo',
        'title': 'Open Opportunities',
        'type': 'search',
        'query_search': 'FIND @ IN ALL FIELDS RETURNING Opportunity (Id, Name, StageName, CloseDate) WITH METADATA=\'LABELS\''
    },
    {
        'keyword': 'co',
        'title': 'Closed Opportunities',
        'type': 'search',
        'query_search': ''
    },
    {
        'keyword': 'wo',
        'title': 'Won Opportunities',
        'type': 'search',
        'query_search': ''
    },
    {
        'keyword': 'oof',
        'title': 'Open Opportunities of',
        'type': 'list',
        'query_options': ''
    },

]

access_token = None

def get_object_url(instance_url, object_id, use_classic = False):
    if use_classic == True:
        return "%s/%s" % (instance_url, object_id)
    else:
        return "%s/one/one.app#/sObject/%s/view" % (instance_url, object_id)

def main(wf):

    # Add a notification if upgrade available
    if wf.update_available:
        wf.add_item(
            'New version available',
            'Action this to install the update',
            autocomplete='workflow:update',
            icon=ICON_INFO
        )

    # Get query from Alfred
    if len(wf.args):
        query = wf.args[0]
    else:
        query = ''

    # Splitting query
    query_split = query.split()
    if len(query_split) > 0:
        query_0 = query_split[0]
    else:
        query_0 = None
    if len(query_split) > 1:
        query_1 = query_split[1]
    else:
        query_1 = None

    # Trimming full query
    query = query.strip()

    # Trying to get access_token
    try:
        access_token = wf.get_password('access_token')
        refresh_token = wf.get_password('refresh_token')
        instance_url = wf.get_password('instance_url')
    except PasswordNotFound:
        access_token = None
        refresh_token = None
        instance_url = None

    if query_0 == '>':

        for s in SETTINGS:
            if query_1 is None or s['arg'].startswith(query_1.lower()):
                wf.add_item(
                    title=s['title'],
                    arg=s['arg'],
                    icon=s['icon'],
                    autocomplete=s['autocomplete'],
                    valid=True
                )

    elif access_token is None:

        wf.add_item(
            'No configuration for Salesforce.',
            'Type "sf > login" to set your Salesforce account.',
            valid=False,
            icon=ICON_ERROR,
            autocomplete= '> login'
        )

    elif query_0 is not None and len(query)>1:

        sf = salesforce_api.Salesforce(wf, access_token, refresh_token, instance_url)

        results = sf.api_call('/services/data/v40.0/search/', parameters={
            'q': "FIND {%s} IN ALL FIELDS RETURNING Account (Id, Name, Type), Opportunity (Id, Name, StageName, CloseDate), Contact (Id, Name, Email), Lead (Id, Name) WITH METADATA='LABELS' " % query.replace("\\", "\\\\").replace("'", "\\'")
        })

        for r in results.get('searchRecords', []):

            use_classic = wf.settings.get("use_classic", False)

            if r.get("attributes").get("type") == "Account":
                sub = r.get("Type")
                url = get_object_url(instance_url, r.get("Id"), use_classic)
                ico = './account.png'
            elif r.get("attributes").get("type") == "Contact":
                sub = r.get("Email")
                url = get_object_url(instance_url, r.get("Id"), use_classic)
                ico = './contact.png'
            elif r.get("attributes").get("type") == "Opportunity":
                sub = "%s %s" % (r.get("StageName"), r.get("CloseDate"))
                url = get_object_url(instance_url, r.get("Id"), use_classic)
                ico = './opportunity.png'
            elif r.get("attributes").get("type") == "Lead":
                sub = ""
                url = get_object_url(instance_url, r.get("Id"), use_classic)
                ico = './lead.png'

            wf.add_item(
                title="%s (%s)" % (r.get("Name"), r.get("attributes").get("type")),
                subtitle=sub,
                arg=url,
                valid=True,
                icon=ico
            )

        if (len(results.get('searchRecords', []))) == 0:
            wf.add_item(
                "No result for: %s" % query
            )

    else:
        wf.add_item(
            "Type at least two characters to search on Salesforce."
        )

    wf.send_feedback()
    return 0

if __name__ == "__main__":
    wf = Workflow(update_settings={
        'github_slug': 'jereze/alfred-salesforce',
        'frequency': 5,
    })
    sys.exit(wf.run(main))
