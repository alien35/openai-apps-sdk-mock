import unittest

from insurance_server_python.main import (
    _normalize_enum_value,
    RESIDENCY_TYPE_MAPPINGS,
)


class ResidencyTypeMappingsTests(unittest.TestCase):
    def test_aliases_normalize_to_home(self) -> None:
        aliases = [
            "Owner",
            "owned",
            "House",
            "single family",
            "primary residence",
        ]

        for alias in aliases:
            with self.subTest(alias=alias):
                normalized = _normalize_enum_value(alias, RESIDENCY_TYPE_MAPPINGS)
                self.assertEqual(normalized, "Home")

    def test_aliases_normalize_to_apartment(self) -> None:
        aliases = [
            "Apartment",
            "apt",
            "Apartment Unit",
            "flat",
        ]

        for alias in aliases:
            with self.subTest(alias=alias):
                normalized = _normalize_enum_value(alias, RESIDENCY_TYPE_MAPPINGS)
                self.assertEqual(normalized, "Apartment")

    def test_aliases_normalize_to_condo(self) -> None:
        aliases = [
            "Condo",
            "condominium",
        ]

        for alias in aliases:
            with self.subTest(alias=alias):
                normalized = _normalize_enum_value(alias, RESIDENCY_TYPE_MAPPINGS)
                self.assertEqual(normalized, "Condo")

    def test_aliases_normalize_to_mobile_home(self) -> None:
        aliases = [
            "Mobile Home",
            "mobile",
            "Trailer",
            "manufactured home",
        ]

        for alias in aliases:
            with self.subTest(alias=alias):
                normalized = _normalize_enum_value(alias, RESIDENCY_TYPE_MAPPINGS)
                self.assertEqual(normalized, "Mobile Home")

    def test_aliases_normalize_to_fixed_mobile_home(self) -> None:
        aliases = [
            "Fixed Mobile Home",
            "fixed manufactured home",
            "Permanent Mobile Home",
        ]

        for alias in aliases:
            with self.subTest(alias=alias):
                normalized = _normalize_enum_value(alias, RESIDENCY_TYPE_MAPPINGS)
                self.assertEqual(normalized, "Fixed Mobile Home")


if __name__ == "__main__":
    unittest.main()
