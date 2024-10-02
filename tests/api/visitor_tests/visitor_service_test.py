import pytest

from openday_scavenger.api.visitors.exceptions import VisitorUIDInvalidError
from openday_scavenger.api.visitors.schemas import VisitorPoolCreate
from openday_scavenger.api.visitors.service import (
    check_out,
    create,
    create_visitor_pool,
    get_all,
    get_visitor_pool,
)


def test_create_unknown_visitor(empty_db):
    """
    Test the attempt to create a visitor with an unknown UID.

    This test attempts to create a visitor with a UID that does not exist in the visitor pool.
    It verifies that the appropriate exception (VisitorUIDInvalidError) is raised with the correct message.

    Args:
        empty_db (Session): The database fixture that provides an empty database.

    Asserts:
        Raises VisitorUIDInvalidError with the message indicating the UID is not in the visitor pool.
    """

    unknown_uid = "notuid"
    with pytest.raises(VisitorUIDInvalidError, match=f"UID {unknown_uid} not in visitor pool"):
        _ = create(empty_db, visitor_uid=unknown_uid)


def test_visitor_pool(empty_db, number_of_entries=5):
    """
    Test the visitor pool creation and retrieval.

    This test creates a visitor pool with a specified number of entries and verifies that the correct
    number of visitor UIDs are returned. It also tests the retrieval of a limited number of visitor UIDs.

    Args:
        empty_db (Session): The database fixture that provides an empty database.
        number_of_entries (int): The number of entries to create in the visitor pool (default is 5).

    Asserts:
        The number of visitor UIDs returned matches the number of entries created.
        The number of visitor UIDs returned with a limit of 1 is 1.
    """

    create_visitor_pool(empty_db, VisitorPoolCreate(number_of_entries=number_of_entries))
    visitor_uids = get_visitor_pool(empty_db)
    assert len(visitor_uids) == number_of_entries
    visitor_uids = get_visitor_pool(empty_db, limit=1)
    assert len(visitor_uids) == 1


def test_create_visitor(empty_db):
    """
    Test the creation of a visitor from the visitor pool.

    This test creates a visitor pool with one entry, retrieves the UID of the visitor,
    and attempts to create a visitor with that UID. It verifies that the visitor is created
    with the correct UID and is not checked out.

    Args:
        empty_db (Session): The database fixture that provides an empty database.

    Asserts:
        The visitor's UID matches the retrieved UID.
        The visitor is not checked out.
    """

    create_visitor_pool(empty_db, VisitorPoolCreate(number_of_entries=1))
    visitor_uid = get_visitor_pool(empty_db, limit=1)[0].uid
    visitor = create(empty_db, visitor_uid=visitor_uid)
    assert visitor.uid == visitor_uid
    assert not visitor.is_checked_out


def test_checkout_visitor(empty_db):
    """
    Test the checkout process of a visitor.

    This test creates a visitor pool with one entry, retrieves the UID of the visitor,
    creates the visitor, and then checks out the visitor. It verifies that the visitor
    is marked as checked out and that there are no visitors (of which there is only one)
    still playing.

    Args:
        empty_db (Session): The database fixture that provides an empty database.

    Asserts:
        The visitor is marked as checked out.
        There are no visitors still playing.
    """

    create_visitor_pool(empty_db, VisitorPoolCreate(number_of_entries=1))
    visitor_uid = get_visitor_pool(empty_db, limit=1)[0].uid
    _ = create(empty_db, visitor_uid=visitor_uid)
    check_out(empty_db, visitor_uid=visitor_uid)
    visitor = get_all(empty_db, visitor_uid)[0][0]
    assert visitor.is_checked_out
    visitor = get_all(empty_db, still_playing=True)
    assert len(visitor) == 0
