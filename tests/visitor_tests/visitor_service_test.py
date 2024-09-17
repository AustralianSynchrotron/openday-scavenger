from openday_scavenger.api.visitors.schemas import VisitorPoolCreate
from openday_scavenger.api.visitors.service import (
    check_out,
    create,
    create_visitor_pool,
    get_all,
    get_visitor_pool,
)


def test_visitor_pool(empty_db, number_of_entries=5):
    create_visitor_pool(empty_db, VisitorPoolCreate(number_of_entries=number_of_entries))
    visitor_uids = get_visitor_pool(empty_db)
    assert len(visitor_uids) == number_of_entries
    visitor_uids = get_visitor_pool(empty_db, limit=1)
    assert len(visitor_uids) == 1


def test_create_visitor(empty_db):
    create_visitor_pool(empty_db, VisitorPoolCreate(number_of_entries=1))
    visitor_uid = get_visitor_pool(empty_db, limit=1)[0].uid
    visitor = create(empty_db, visitor_uid=visitor_uid)
    assert visitor.uid == visitor_uid
    assert not visitor.is_checked_out


def test_checkout_visitor(empty_db):
    create_visitor_pool(empty_db, VisitorPoolCreate(number_of_entries=1))
    visitor_uid = get_visitor_pool(empty_db, limit=1)[0].uid
    _ = create(empty_db, visitor_uid=visitor_uid)
    check_out(empty_db, visitor_uid=visitor_uid)
    visitor = get_all(empty_db, visitor_uid)[0][0]
    assert visitor.is_checked_out
    visitor = get_all(empty_db, still_playing=True)
    assert len(visitor) == 0
