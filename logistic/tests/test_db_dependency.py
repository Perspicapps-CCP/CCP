import pytest
from unittest.mock import MagicMock, patch
from db_dependency import get_db


@pytest.fixture
def mock_session() -> MagicMock:
    """Fixture that provides a mock database session."""
    mock = MagicMock()
    return mock


@patch("db_dependency.SessionLocal")
def test_get_db_yields_session(
    mock_session_local, mock_session: MagicMock
) -> None:
    """Test that get_db yields a database session."""
    mock_session_local.return_value = mock_session
    db = next(get_db())
    mock_session_local.assert_called_once()

    assert db == mock_session

    try:
        next(get_db())
    except StopIteration:
        pass


@patch("db_dependency.SessionLocal")
def test_get_db_closes_session(
    mock_session_local, mock_session: MagicMock
) -> None:
    """Test that get_db closes the database session."""
    mock_session_local.return_value = mock_session

    with pytest.raises(StopIteration):
        gen = get_db()
        next(gen)
        next(gen)

    mock_session.close.assert_called_once()
