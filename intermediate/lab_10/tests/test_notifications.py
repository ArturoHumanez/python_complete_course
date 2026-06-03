from unittest.mock import patch

import httpx

from intermediate.lab_10.notifications import process_new_order


class TestProcessNewOrder:
    @patch("intermediate.lab_10.notifications.send_order_notification")
    def test_order_confirmed_when_notification_succeeds(self, mock_notify):
        mock_notify.return_value = True

        result = process_new_order(1, "Juan", 25000)

        assert result["status"] == "confirmed"
        assert result["notified"] is True
        mock_notify.assert_called_once_with(1, "Juan", 25000)

    @patch("intermediate.lab_10.notifications.send_order_notification")
    def test_order_confirmed_even_when_notification_fails(self, mock_notify):
        mock_notify.return_value = False

        result = process_new_order(1, "Juan", 25000)

        assert result["status"] == "confirmed"
        assert result["notified"] is False

    @patch("intermediate.lab_10.notifications.httpx.post")
    def test_send_notification_http_error(self, mock_post):
        mock_post.side_effect = httpx.RequestError("Connection refused")

        result = process_new_order(1, "Juan", 25000)

        assert result["notified"] is False