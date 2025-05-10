from datetime import datetime
from whois import whois
import sys
import os
sys.path.append(os.path.abspath(os.path.join('..')))


def get_domain_info(url: str):
    '''
    Uses whois to get information about the domain
    '''
    domain_age = 0
    status = 0
    try:
        res = whois(url)
        domain_age = get_domain_age(res.creation_date)
        status = get_domain_status(res.status)
    except Exception as e:
        pass
    return {
        'domain_age': domain_age,
        'domain_status': status
    }


def get_domain_age(date: datetime | list[datetime] | None) -> int:
    if not date:
        return 0
    if isinstance(date, list):
        date = date[0]
    return (datetime.now() - date).days


def get_domain_status(status: str | None | list[str]) -> int:
    '''
    A limited check on the status of the domain
    '''
    weak_statuses = {'ok', 'pendingdelete',
                     'pendingcreate', 'serverhold', 'inactive'}
    if not status:
        return 0

    if isinstance(status, str):
        return 1 if status.lower() in weak_statuses else 2

    if isinstance(status, list):
        if any(s.lower() in weak_statuses for s in status):
            return 1
    return 2


if __name__ == '__main__':
    print(get_domain_info('google.com'))
    print(get_domain_info('https://mail.yahoo.com/n/search/accountIds=1?listFilter=PRIORITY&guce_referrer=aHR0cHM6Ly9sb2dpbi55YWhvby5jb20v&guce_referrer_sig=AQAAACTBxTPzZE6pBSb-SM1y81N90xYdrUtgxoEaIiWlYcr3JQlMX1jGdRFpMohUxq42GjZWfbUw9TnwL5KS-kDLnEOLnxD3wxQz3pxL3YqfQMs5zcnHQ5V_JMYcs5HQUWmCHyJOdAyiA0DrY_JmQTUfJuRQko'))
