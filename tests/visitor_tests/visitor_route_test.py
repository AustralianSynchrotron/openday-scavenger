from fastapi import status

from openday_scavenger.api.visitors.schemas import VisitorCreate, VisitorPoolCreate
from openday_scavenger.api.visitors.service import create_visitor_pool, get_visitor_pool


def test_visitor_pool(mock_client):
    response = mock_client.post("/admin/visitors/pool")
    assert response.status_code == status.HTTP_200_OK


def test_create_user(empty_db, mock_client):
    create_visitor_pool(empty_db, VisitorPoolCreate(number_of_entries=1))
    visitor_uid = get_visitor_pool(empty_db, limit=1)[0].uid
    VisitorCreate(uid=visitor_uid)
    response = mock_client.post(
        "/admin/visitors/", json=VisitorCreate(uid=visitor_uid).model_dump()
    )
    assert response.status_code == status.HTTP_200_OK
