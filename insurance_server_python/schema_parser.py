"""Schema parser for zrater.io API contracts.

This module fetches and parses JSON Schema contracts from the zrater.io API
to determine required fields for minimal form collection.
"""

import logging
import os
from typing import Any, Dict, List, Set, Optional
import httpx

logger = logging.getLogger(__name__)


class SchemaParser:
    """Parses zrater.io JSON Schema contracts to extract required fields."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.contracts: Dict[str, Dict[str, Any]] = {}

    async def fetch_contract(self, state: str) -> Dict[str, Any]:
        """Fetch the contract schema for a given state.

        Args:
            state: Two-letter state code (e.g., "CA")

        Returns:
            The parsed contract schema
        """
        url = f"https://gateway.zrater.io/api/v1/linesOfBusiness/personalAuto/states/{state}/contracts"
        headers = {
            "x-api-key": self.api_key,
            "Content-Length": "0"
        }

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                contracts_list = response.json()

                if not contracts_list:
                    raise ValueError(f"No contracts found for state {state}")

                # Get the most recent contract (first in list)
                contract_data = contracts_list[0]
                contract = contract_data.get("contract", {})

                logger.info(f"Fetched contract for {state}: version {contract_data.get('version')}")
                self.contracts[state] = contract
                return contract

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch contract for {state}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing contract for {state}: {e}")
            raise

    def get_required_fields(self, schema: Dict[str, Any], path: str = "") -> Dict[str, Any]:
        """Extract required fields from a JSON Schema definition.

        Args:
            schema: The JSON Schema object
            path: The current path in the schema (for nested objects)

        Returns:
            Dictionary mapping field paths to their requirements
        """
        required_fields = {}

        # Get the required array at this level
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        definitions = schema.get("definitions", {})

        for field_name in required:
            field_path = f"{path}.{field_name}" if path else field_name
            field_schema = properties.get(field_name, {})

            required_fields[field_path] = {
                "type": field_schema.get("type"),
                "description": field_schema.get("description"),
                "enum": field_schema.get("enum"),
                "format": field_schema.get("format"),
                "pattern": field_schema.get("pattern"),
                "minimum": field_schema.get("minimum"),
                "maximum": field_schema.get("maximum"),
            }

            # Handle $ref references to definitions
            if "$ref" in field_schema:
                ref_path = field_schema["$ref"]
                if ref_path.startswith("#/definitions/"):
                    def_name = ref_path.split("/")[-1]
                    if def_name in definitions:
                        # Recursively get required fields from the referenced definition
                        nested = self.get_required_fields(definitions[def_name], field_path)
                        required_fields.update(nested)

            # Handle nested objects
            elif field_schema.get("type") == "object" and "properties" in field_schema:
                nested = self.get_required_fields(field_schema, field_path)
                required_fields.update(nested)

            # Handle arrays of objects
            elif field_schema.get("type") == "array":
                items = field_schema.get("items", {})
                if "$ref" in items:
                    ref_path = items["$ref"]
                    if ref_path.startswith("#/definitions/"):
                        def_name = ref_path.split("/")[-1]
                        if def_name in definitions:
                            nested = self.get_required_fields(definitions[def_name], f"{field_path}[]")
                            required_fields.update(nested)

        return required_fields

    def get_minimal_fields_for_state(self, state: str) -> Dict[str, Any]:
        """Get the minimal required fields configuration for a state.

        Args:
            state: Two-letter state code (e.g., "CA")

        Returns:
            Dictionary of minimal required fields organized by section
        """
        if state not in self.contracts:
            raise ValueError(f"No contract loaded for state {state}. Call fetch_contract() first.")

        contract = self.contracts[state]
        definitions = contract.get("definitions", {})

        # Extract required fields from each major section
        minimal_fields = {
            "customer": {},
            "driver": {},
            "vehicle": {},
            "policy_coverages": {},
            "metadata": {}
        }

        # Customer fields
        if "Customer" in definitions:
            minimal_fields["customer"] = self.get_required_fields(definitions["Customer"])

        # Driver fields
        if "Driver" in definitions:
            minimal_fields["driver"] = self.get_required_fields(definitions["Driver"])

        # Vehicle fields
        if "Vehicle" in definitions:
            minimal_fields["vehicle"] = self.get_required_fields(definitions["Vehicle"])

        # Policy coverages
        if "PolicyCoverages" in definitions:
            minimal_fields["policy_coverages"] = self.get_required_fields(definitions["PolicyCoverages"])

        return minimal_fields

    def get_conditional_requirements(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract conditional requirements (if/then logic) from schema.

        Args:
            schema: The JSON Schema object

        Returns:
            List of conditional requirement rules
        """
        conditionals = []

        # Check for allOf with if/then patterns
        for condition in schema.get("allOf", []):
            if "if" in condition and "then" in condition:
                if_props = condition["if"].get("properties", {})
                then_required = condition["then"].get("required", [])

                conditionals.append({
                    "if": if_props,
                    "then_required": then_required
                })

        # Check for anyOf patterns
        for condition in schema.get("anyOf", []):
            if "if" in condition and "then" in condition:
                if_props = condition["if"].get("properties", {})
                then_required = condition["then"].get("required", [])

                conditionals.append({
                    "if": if_props,
                    "then_required": then_required
                })

        return conditionals


# Global instance
_schema_parser: Optional[SchemaParser] = None


async def initialize_schema_parser(api_key: str, states: List[str] = ["CA"]) -> SchemaParser:
    """Initialize the global schema parser and fetch contracts.

    Args:
        api_key: zrater.io API key
        states: List of state codes to fetch contracts for

    Returns:
        Initialized SchemaParser instance
    """
    global _schema_parser

    _schema_parser = SchemaParser(api_key)

    for state in states:
        try:
            await _schema_parser.fetch_contract(state)
            logger.info(f"Loaded contract for {state}")
        except Exception as e:
            logger.error(f"Failed to load contract for {state}: {e}")

    return _schema_parser


def get_schema_parser() -> SchemaParser:
    """Get the global schema parser instance.

    Returns:
        The initialized SchemaParser

    Raises:
        RuntimeError: If parser not initialized
    """
    if _schema_parser is None:
        raise RuntimeError("Schema parser not initialized. Call initialize_schema_parser() first.")
    return _schema_parser
