import pytest

from bustransporter import auth, db, users


@pytest.fixture
def conn():
    return db.connect()


@pytest.fixture
def admin(conn):
    admin_id = users.create_user(conn, {"id": 0, "role": "admin"}, "root", "rootpw", "admin")
    return auth.login(conn, "root", "rootpw") | {"id": admin_id}


@pytest.fixture
def engineer(conn, admin):
    users.create_user(conn, admin, "ivan", "secret", "engineer")
    return auth.login(conn, "ivan", "secret")


def test_admin_creates_user_who_can_log_in(conn, admin):
    users.create_user(conn, admin, "maria", "pw", "engineer")
    assert auth.login(conn, "maria", "pw")["role"] == "engineer"


def test_list_users(conn, admin, engineer):
    assert [u["username"] for u in users.list_users(conn, admin)] == ["ivan", "root"]


def test_admin_changes_role_and_password(conn, admin, engineer):
    users.update_user(conn, admin, engineer["id"], role="admin", password="new")
    assert auth.login(conn, "ivan", "new")["role"] == "admin"


def test_admin_deletes_user(conn, admin, engineer):
    users.delete_user(conn, admin, engineer["id"])
    with pytest.raises(auth.LoginError):
        auth.login(conn, "ivan", "secret")


def test_duplicate_username_is_rejected(conn, admin, engineer):
    with pytest.raises(users.UserError):
        users.create_user(conn, admin, "ivan", "other", "engineer")


def test_invalid_role_is_rejected(conn, admin):
    with pytest.raises(users.UserError):
        users.create_user(conn, admin, "guest", "pw", "guest")


@pytest.mark.parametrize("operation", [
    lambda c, actor, target: users.list_users(c, actor),
    lambda c, actor, target: users.create_user(c, actor, "x", "pw", "engineer"),
    lambda c, actor, target: users.update_user(c, actor, target, role="admin"),
    lambda c, actor, target: users.delete_user(c, actor, target),
])
def test_engineer_has_no_access(conn, admin, engineer, operation):
    with pytest.raises(users.AccessDenied):
        operation(conn, engineer, admin["id"])


def test_admin_cannot_delete_self(conn, admin):
    with pytest.raises(users.UserError):
        users.delete_user(conn, admin, admin["id"])
