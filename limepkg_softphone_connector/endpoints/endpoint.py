import lime_webserver.webserver as webserver
import logging
import lime_config
from ..endpoints import api
from flask import redirect
from lime_query import execute_query
from lime_query.query_builder import QueryBuilder
import phonenumbers

logger = logging.getLogger(__name__)


class OpenCustomer(webserver.LimeResource):
    '''
    This endpoint is called by a Softphone supplier in order to open a either
    a person or company card in the webclient.
    The library "phonenumbers" is required to run the code.
    '''

    def get(self, callingnumber):
        '''
        This takes the incoming number, gets nationalnumber if there is a
        country code, and looks up callingnumber (with potential country code)
        and nationalnumber.
        Config should have limetypes with database names of fields that holds
        a number. The number calling is then looked up on the written limetypes
        and fields. If object can't be found, it redirects to search.
        TODO make it create a company/person instead of redirecting to search?
        '''
        app = self.application
        config = lime_config.get_app_config(app, 'config.softphone')
        nationalnumber = get_national_number(callingnumber)
        callingnumber = format_phone_number(callingnumber)

        for limetype in config.limetypes:
            properties = config.limetypes.get(limetype)

            if isinstance(properties, str):
                properties = [properties]

            for property in properties:
                idobject = get_idobject(app,
                                        limetype,
                                        property,
                                        callingnumber,
                                        nationalnumber)

                if idobject:
                    return redirect(
                        'https://{}/client/object/{}/{}'.format(
                            config.hostname,
                            limetype,
                            idobject
                        ),
                        code=302
                    )

        # If no match, redirect to main search
        return redirect(
            f'https://{config.hostname}/client/search',
            code=302
        )


def get_customer_id(app, limetype, property, phone_number):
    qb = QueryBuilder(app, limetype)
    qb.add_field(property)
    query = qb.query
    query['limit'] = 0
    query['filter'] = {
        'op': 'AND',
        'exp': [
            {'key': property, 'op': '?', 'exp': phone_number}
        ]
    }
    res = execute_query(
        query=query,
        conn=app.database.connection,
        limetypes=app.limetypes,
        acl=app.acl,
        user=app.user
        )

    return res['objects'][0]['_id'] if res['objects'] else None


def format_phone_number(phone_number: str):
    '''Will remove leading zero'''
    if phone_number.startswith('0'):
        return phone_number[1:]

    return phone_number


def get_national_number(callingnumber: str):
    try:
        phonenumber = phonenumbers.parse(callingnumber, None)
        nationalnumber = str(phonenumber.national_number)
        return nationalnumber
    except phonenumbers.NumberParseException:
        # If parsing fails, we use the calling number as it is
        pass

    return None


def get_idobject(app,
                 limetype,
                 property,
                 callingnumber: str,
                 nationalnumber: str = None):

    idobject = get_customer_id(app=app,
                               limetype=limetype,
                               property=property,
                               phone_number=callingnumber)

    if not idobject and nationalnumber:
        idobject = get_customer_id(app=app,
                                   limetype=limetype,
                                   property=property,
                                   phone_number=nationalnumber)

    return idobject


api.add_resource(OpenCustomer, '/callanswered/<string:callingnumber>')