import json
import sys
import tempfile
import types
import unittest
from datetime import timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    ZoneInfo("Asia/Seoul")
except ZoneInfoNotFoundError:
    import zoneinfo

    zoneinfo.ZoneInfo = lambda _key: timezone(timedelta(hours=9))

try:
    import playwright.sync_api  # noqa: F401
except ModuleNotFoundError:
    playwright = types.ModuleType("playwright")
    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.Page = object
    sync_api.TimeoutError = TimeoutError
    sync_api.sync_playwright = None
    playwright.sync_api = sync_api
    sys.modules["playwright"] = playwright
    sys.modules["playwright.sync_api"] = sync_api

import update_getcha_prices


class UpdateGetchaPricesTests(unittest.TestCase):
    def test_matched_prices_are_updated_while_unmatched_prices_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app_path = root / "app.html"
            state_path = root / "getcha-price-state.json"
            data = {
                "prices": {
                    "Hyundai": {
                        "Premium": {
                            "msrp": 10,
                            "promo": 0,
                            "total": 10,
                            "discountedPrice": 10,
                            "promotionCheckedAt": "2026-10-01",
                        }
                    },
                    "Tesla": {
                        "Model Y L": {
                            "msrp": 20,
                            "promo": 0,
                            "total": 20,
                            "discountedPrice": 20,
                            "promotionCheckedAt": "2026-10-01",
                        }
                    },
                }
            }
            app_path.write_text(
                "<script>window.ES90_DATA = "
                + json.dumps(data, ensure_ascii=False)
                + ";</script>",
                encoding="utf-8",
            )
            prices = {
                ("Hyundai", "Premium"): {
                    "msrp": 100,
                    "promo": 10,
                    "discountedPrice": 90,
                    "modelYear": 27,
                }
            }
            unmatched = ["Tesla / Model Y L: exact match failed"]

            with (
                patch.object(update_getcha_prices, "APP_PATH", app_path),
                patch.object(update_getcha_prices, "STATE_PATH", state_path),
            ):
                changed, checked_at = update_getcha_prices.update_app(
                    prices, unmatched
                )

            updated_text = app_path.read_text(encoding="utf-8")
            embedded = json.loads(
                updated_text.split("window.ES90_DATA = ", 1)[1].split(
                    ";</script>", 1
                )[0]
            )
            matched = embedded["prices"]["Hyundai"]["Premium"]
            preserved = embedded["prices"]["Tesla"]["Model Y L"]
            state = json.loads(state_path.read_text(encoding="utf-8"))

            self.assertEqual(changed, ["Hyundai / Premium"])
            self.assertEqual(matched["msrp"], 100)
            self.assertEqual(matched["promo"], 10)
            self.assertEqual(matched["discountedPrice"], 90)
            self.assertEqual(matched["modelYear"], 27)
            self.assertEqual(matched["promotionCheckedAt"], checked_at)
            self.assertRegex(checked_at, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
            self.assertEqual(preserved["msrp"], 20)
            self.assertEqual(preserved["promotionCheckedAt"], "2026-10-01")
            self.assertEqual(state["matchedTrimCount"], 1)
            self.assertEqual(state["unmatchedTrimCount"], 1)
            self.assertEqual(state["unmatchedTrims"], unmatched)

    def test_newest_section_uses_getcha_model_year(self) -> None:
        sections = [
            {"title": "테슬라 모델 Y (26년식)", "text": "old"},
            {"title": "테슬라 모델 Y (27년식)", "text": "new"},
        ]

        selected = update_getcha_prices.newest_section(
            sections, "테슬라 모델 Y"
        )

        self.assertEqual(selected["text"], "new")
        self.assertEqual(update_getcha_prices.section_model_year(selected), 27)

    def test_tesla_model_y_uses_latest_longwheelbase_grade(self) -> None:
        self.assertIn(
            (
                "테슬라",
                "테슬라 모델 Y",
                "L 프리미엄 AWD",
                "Tesla",
                "Model Y L",
            ),
            update_getcha_prices.MATCHES,
        )


if __name__ == "__main__":
    unittest.main()
