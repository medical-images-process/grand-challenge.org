import pytest

from tests.factories import PatientFactory
from tests.utils import get_view_for_user


@pytest.mark.django_db
def test_patient_list(client):
    visible = PatientFactory(hidden=False)
    invisible = PatientFactory(hidden=True)

    response = get_view_for_user(client=client, viewname="patients:patient-list")

    assert visible.short_name in response.rendered_content
    assert invisible.short_name not in response.rendered_content
