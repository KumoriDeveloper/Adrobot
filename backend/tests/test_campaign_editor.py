import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.services.campaign_editor import (
    _normalize_offers,
    add_offer,
    remove_offer,
)


class NormalizeOffersTests(unittest.TestCase):
    def test_share_distribution(self):
        expected = {
            1: [100],
            2: [50, 50],
            3: [34, 33, 33],
            4: [25, 25, 25, 25],
            5: [20, 20, 20, 20, 20],
        }

        for count, shares in expected.items():
            with self.subTest(count=count):
                offers = [
                    {"offer_id": 1000 + i, "state": "active"}
                    for i in range(count)
                ]

                result = _normalize_offers(offers)

                self.assertEqual(
                    [offer["share"] for offer in result],
                    shares,
                )
                self.assertEqual(sum(o["share"] for o in result), 100)

    def test_empty_offers(self):
        self.assertEqual(_normalize_offers([]), [])

    def test_preserves_offer_state(self):
        result = _normalize_offers([
            {"offer_id": 1001, "state": "paused"},
        ])

        self.assertEqual(result, [
            {"offer_id": 1001, "share": 100, "state": "paused"},
        ])


class CampaignOfferTests(unittest.IsolatedAsyncioTestCase):
    def make_client(self, offers):
        client = Mock()
        client.list_streams = AsyncMock(return_value=[
            {"id": 523, "type": "default"},
        ])
        client.get_stream = AsyncMock(return_value={
            "id": 523,
            "offers": offers,
        })
        client.update_stream = AsyncMock()
        return client

    async def test_add_offer_recalculates_shares(self):
        client = self.make_client([
            {"offer_id": 18104, "share": 100, "state": "active"},
        ])

        with patch(
            "app.services.campaign_editor.KeitaroClient",
            return_value=client,
        ):
            result = await add_offer(272, 18105)

        self.assertEqual(result["message"], "Оффер добавлен")
        self.assertEqual(
            [o["share"] for o in result["offers"]],
            [50, 50],
        )
        self.assertEqual(result["total_share"], 100)
        client.update_stream.assert_awaited_once_with(523, {
            "offers": [
                {"offer_id": 18104, "share": 50, "state": "active"},
                {"offer_id": 18105, "share": 50, "state": "active"},
            ],
        })

    async def test_duplicate_offer_is_not_added(self):
        client = self.make_client([
            {"offer_id": 18104, "share": 100, "state": "active"},
        ])

        with patch(
            "app.services.campaign_editor.KeitaroClient",
            return_value=client,
        ):
            result = await add_offer(272, 18104)

        self.assertEqual(result["message"], "Оффер уже существует")
        self.assertEqual(len(result["offers"]), 1)
        client.update_stream.assert_not_awaited()

    async def test_remove_offer_recalculates_shares(self):
        client = self.make_client([
            {"offer_id": 18104, "share": 50, "state": "active"},
            {"offer_id": 18105, "share": 50, "state": "active"},
        ])

        with patch(
            "app.services.campaign_editor.KeitaroClient",
            return_value=client,
        ):
            result = await remove_offer(272, 18105)

        self.assertEqual(result["message"], "Оффер удалён")
        self.assertEqual(result["offers"], [
            {"offer_id": 18104, "share": 100, "state": "active"},
        ])
        self.assertEqual(result["total_share"], 100)

    async def test_remove_missing_offer_does_not_update(self):
        client = self.make_client([
            {"offer_id": 18104, "share": 100, "state": "active"},
        ])

        with patch(
            "app.services.campaign_editor.KeitaroClient",
            return_value=client,
        ):
            result = await remove_offer(272, 99999)

        self.assertEqual(result["message"], "Оффер не найден")
        client.update_stream.assert_not_awaited()

    async def test_remove_last_offer(self):
        client = self.make_client([
            {"offer_id": 18104, "share": 100, "state": "active"},
        ])

        with patch(
            "app.services.campaign_editor.KeitaroClient",
            return_value=client,
        ):
            result = await remove_offer(272, 18104)

        self.assertEqual(result["offers"], [])
        self.assertEqual(result["total_share"], 0)
        client.update_stream.assert_awaited_once_with(
            523,
            {"offers": []},
        )

    async def test_non_positive_offer_id_is_rejected(self):
        with self.assertRaises(ValueError):
            await add_offer(272, 0)

        with self.assertRaises(ValueError):
            await remove_offer(272, -1)


if __name__ == "__main__":
    unittest.main()
