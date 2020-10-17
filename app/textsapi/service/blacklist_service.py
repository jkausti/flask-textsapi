import datetime

from ..models.blacklist import BlacklistedToken


def save_token(token, username):
    try:
        blacklist_token = BlacklistedToken(
            username = username,
            sort = create_sort_attr(),
            token = token,
            blacklisted_on = datetime.datetime.utcnow()
        )
        blacklist_token.save()
        response_object = {
            'status': 'success',
            'message': 'successfully logged out'
        }
        return response_object, 200
    except Exception as e:
        return {
            'status': 'failed',
            'message': e
        }

"""
HELPER FUNCTIONS
"""

def create_sort_attr():
    new_sort = 'TOKEN_1'
    new_id = int(new_sort.split('_')[1])
    scan_filter = BlacklistedToken.sort.contains('TOKEN')

    for t in BlacklistedToken.scan(filter_condition=scan_filter, attributes_to_get=BlacklistedToken.sort):
        id = int(t.split('_')[1])
        if id >= new_id:
            new_id = id + 1
    
    return "TOKEN_" + str(new_id)