from fastapi import status

from openday_scavenger.api.visitors.schemas import VisitorCreate, VisitorPoolCreate
from openday_scavenger.api.visitors.service import create_visitor_pool, get_visitor_pool


def test_create_unknown_user(mock_client):
    """
    Test the creation of a visitor with an unknown UID.

    This test attempts to create a visitor with a UID that does not exist in the visitor pool.
    It verifies that the response status code is 404 NOT FOUND.

    Args:
        mock_client (TestClient): The fastapi test client used to simulate HTTP requests.

    Asserts:
        The response status code is 404 NOT FOUND.
    """

    unknown_uid = "notuid"
    VisitorCreate(uid=unknown_uid)
    response = mock_client.post(
        "/admin/visitors/", json=VisitorCreate(uid=unknown_uid).model_dump()
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_visitor_pool(mock_client):
    """
    Test the create visitor pool endpoint.

    This test sends a POST request to the visitor pool endpoint and verifies that the
    response status code is 200 OK, indicating that a valid pool was created.

    Args:
        mock_client (TestClient): The fastapi test client used to simulate HTTP requests.

    Asserts:
        The response status code is 200 OK.
    """

    response = mock_client.post("/admin/visitors/pool")
    assert response.status_code == status.HTTP_200_OK


def test_create_user(empty_db, mock_client):
    """
    Test the creation of a user from the visitor pool.

    This test creates a visitor pool with one entry, retrieves the UID of the visitor,
    and attempts to create a user with that UID. It verifies that the response status
    code is 200 OK.

    Args:
        empty_db (Session): The database fixture that provides an empty database.
        mock_client (TestClient): The fastapi test client used to simulate HTTP requests.

    Asserts:
        The response status code is 200 OK.
    """

    create_visitor_pool(empty_db, VisitorPoolCreate(number_of_entries=1))
    visitor_uid = get_visitor_pool(empty_db, limit=1)[0].uid
    VisitorCreate(uid=visitor_uid)
    response = mock_client.post(
        "/admin/visitors/", json=VisitorCreate(uid=visitor_uid).model_dump()
    )
    assert response.status_code == status.HTTP_200_OK
