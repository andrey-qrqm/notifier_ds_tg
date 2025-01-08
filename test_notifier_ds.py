from notifier_ds import get_nickname, take_ids, send_data, run_discord_bot
from unittest.mock import MagicMock, patch


def test_get_nickname_with_parentheses():
    assert get_nickname("User (Nickname)") == "Nickname"


def test_get_nickname_without_parentheses():
    assert get_nickname("User") == "User"


def test_take_ids():
    mock_conn = MagicMock()
    mock_cur = mock_conn.cursor.return_value
    mock_cur.fetchall.return_value = [[123456789]]

    result = take_ids("DiscordGuild", mock_conn)
    mock_cur.execute.assert_called_with("""
        SELECT tg_chat_id FROM tracking WHERE DISCORD_ID = 'DiscordGuild' 
    """)
    assert result == [[123456789]]

@patch("psycopg2.connect")
def test_take_ids_with_mocked_db(mock_connect):
    mock_conn = mock_connect.return_value
    mock_cur = mock_conn.cursor.return_value
    mock_cur.fetchall.return_value = [[123456789]]

    result = take_ids("GuildName", mock_conn)
    assert result == [[123456789]]
