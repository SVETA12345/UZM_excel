import pytest
request_url = 'http://127.0.0.1:8000/'
from rest_framework.test import APIClient

# @pytest.fixture(scope='module')  # Фикстура уничтожается после выполнения последнего теста в модуле
# def api_client():
#     """Фикстура для API Client REST фреймворка"""



# @pytest.mark.skip(reason='Тестирование всех url по запросу основных моделей')
@pytest.mark.django_db
@pytest.mark.parametrize(
   'url, status_code', [
       (request_url + 'main_data/api/field/', 200),
       (request_url + 'main_data/api/pad/', 200),
       (request_url + 'main_data/api/run/', 200),
       (request_url + 'main_data/api/section/', 200),
       (request_url + 'main_data/api/well/', 200),
       (request_url + 'main_data/api/wellbore/', 200),
   ]
)
def test_main_data(url, status_code):
    """ Доступность указаных выше адрессов"""
    api_client = APIClient()
    response = api_client.get(url)
    assert response.status_code == status_code
