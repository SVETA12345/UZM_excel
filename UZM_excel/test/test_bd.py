import pytest

from Field.models import *


# @pytest.mark.skip(reason='Создание тестовых записей в бд')
@pytest.mark.django_db
# @pytest.fixture(scope='session', autouse=True)
def test_create_Field():
    c = Client.objects.create(client_name='Test_client')
    f = Field.objects.create(client=c, field_name='Test_field')
    p = Pad.objects.create(field=f, pad_name='Test_pad')
    well = Well.objects.create(pad_name=p, well_name='Test_Well')
    wellbore = Wellbore.objects.create(well_name=well, wellbore='PLT0')
    section = Section.objects.create(wellbore=wellbore, section='Test_section')
    run = Run.objects.create(section=section, run_number='99')
    print(run.id)
    assert str(run) == 'Test_field; Куст.Test_pad; Test_Well; ПЛ; Test_section; 99;'

@pytest.mark.django_db
def test_get_run():
    assert 'Test_field; Куст.Test_pad; Test_Well; ПЛ; Test_section; 99;' == str(Run.objects.get(id=1))