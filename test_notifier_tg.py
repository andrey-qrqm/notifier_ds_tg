import pytest
from unittest.mock import patch, MagicMock
from notifier_tg import remove_spaces, conn_check, extract_arg, create_database_conn


def test_remove_spaces():
    assert remove_spaces("hello world") == "helloworld"
    assert remove_spaces("   ") == ""
    assert remove_spaces("") == ""

def test_extract_arg():
    assert extract_arg("/add_channel test_channel") == ["test_channel"]
    assert extract_arg("") == []

@patch('psycopg2.connect')
def test_conn_check(mock_connect):
    mock_connect.return_value = MagicMock()
    conn_check()
    mock_connect.assert_called_once()

@patch('psycopg2.connect')
def test_create_database_conn(mock_connect):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    create_database_conn()
    mock_conn.cursor().execute.assert_called()