from unittest.mock import MagicMock
import lime_test.app
import lime_test.db
import lime_test.web_app
import pytest
import lime_config
from lime_type import create_limeobjects_from_dsl
from limepkg_softphone_connector.endpoints.endpoint import (
    get_customer_id,
    get_idobject,
    get_national_number,
    format_phone_number
)


def test_return_one_if_one_company_present(webapp, test_limeobjects,
                                           monkeypatch, get_mock_app_config):
    # monkeypatch(lime_config, 'get_app_config', get_mock_app_config)
    res = webapp.get(
        '/myapp/limepkg-softphone-connector/callanswered/123456789')

    assert res.location == 'https://Testen teknik/client/object/person/1'

    res = webapp.get(
        '/myapp/limepkg-softphone-connector/callanswered/9875')

    assert res.location == 'https://Testen teknik/client/search'

    # json_response = json.loads(res.data.decode('utf-8'))

    # assert json_response == {
    #     'message': 'Hello, Kenny! There are 1 objects '
    #     'of type company available'
    # }


def test_get_customer_id(limeapp, test_limeobjects):
    id = get_customer_id(limeapp, 'company', 'phone', 12345678)
    idNone = get_customer_id(limeapp, 'person', 'phone', 13)

    assert id == 1
    assert idNone is None


def test_get_idobject(limeapp, test_limeobjects):
    # matches
    id1 = get_idobject(limeapp, 'company', 'phone', '12345678')
    id2 = get_idobject(limeapp, 'company', 'phone', '+455555555', '55555555')
    id3 = get_idobject(limeapp, 'company', 'phone', '11111111')
    # no matches
    id4 = get_idobject(limeapp, 'person', 'phone', '1212121')

    assert id1 == 1
    assert id2 == 2
    assert id3 == 3
    assert id4 is None


def test_get_national_number():
    number = get_national_number('+451111111')
    error_number = get_national_number('+11')

    assert number == '1111111'
    assert error_number is None


def test_format_phonenumber():
    number = format_phone_number('012345678')
    nozeronumber = format_phone_number('1234')

    assert number == '12345678'
    assert nozeronumber == '1234'


@pytest.fixture
def webapp(limeapp, database, plugins_path, monkeypatch):
    """An in-memory web application where you're authenticated as a user"""
    web_app = lime_test.web_app.create_web_app(database,
                                               plugins_path=plugins_path,
                                               monkeypatch=monkeypatch)

    return lime_test.web_app.create_authenticated_web_client(web_app=web_app,
                                                             app=limeapp,
                                                             username='kenny',
                                                             password='kenny')


@pytest.fixture
def get_mock_app_config(app=None, kw=None):
    class app_conf():
        def __init__(self):
            self.hostname = 'Testen teknik'
            self.limetypes = {
                'person': ['mobilephone', 'phone'],
                'company': 'phone'
                }

    lime_config.get_app_config = MagicMock(
        return_value=app_conf()
    )


@pytest.fixture
def test_limeobjects(limeapp):
    ODSL = '''
    company:
        company1:
            name: test A/S
            phone: '12345678'
        company2:
            name: test A/S1
            phone: '55555555'
        company3:
            name: test A/S2
            phone: '11111111'
    person:
        person:
            firstname: testman1
            phone: '123456789'
    '''

    return create_limeobjects_from_dsl(limeapp.limetypes, ODSL)
