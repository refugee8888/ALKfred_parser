from unittest.mock import patch, MagicMock


def test_postgres_conn_mock():
    with patch("alkfred.config.postgres_conn") as mock_conn:
        mock_conn.return_value = MagicMock()
        conn = mock_conn()
        assert conn is not None


def test_rds_connect_mock():
    with patch("psycopg2.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        import psycopg2
        conn = psycopg2.connect("dbname=alkfred user=alkfred host=alkfred-db.cjgsqkmoajg6.eu-central-1.rds.amazonaws.com port=5432")
        assert conn is not None
        mock_connect.assert_called_once()
