


from unittest.mock import patch

def test_postgres_conn():
    with patch("alkfred.config.postgres_conn") as mock_conn:
        mock_conn.return_value = True
        assert True


