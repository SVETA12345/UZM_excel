import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from Field.models import Run


def test_Run(db):
    assert len(Run.objects.all()) != 0

@pytest.mark.django_db
@pytest.mark.parametrize(
   'rid, status_code', [
       (129, 200),
       (147, 200),
       (201, 200),
   ]
)
def test_get_report(rid, status_code):
    api_client = APIClient()
    response1 = api_client.post(reverse('get_file_name'), {'run_id': rid})
    response2 = api_client.post(reverse('get_report_file'), {'name': response1.data['file_name']}, format='json')
    assert response2.status_code == status_code



