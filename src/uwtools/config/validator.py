"""
Support for validating a config using JSON Schema.
"""

import json
from typing import List

import jsonschema

from uwtools.config.core import YAMLConfig
from uwtools.logging import log
from uwtools.types import DefinitePath, OptionalPath

# Public functions


def validate_yaml(schema_file: DefinitePath, config_file: OptionalPath = None) -> bool:
    """
    Check whether the given config file conforms to the given JSON Schema spec and whether any
    filesystem paths it identifies do not exist.

    :param schema_file: The JSON Schema file to use for validation.
    :param config_file: The YAML file to validate (stdin will be used by default)
    :return: Did the YAML file conform to the schema?
    """
    # Load the config and schema.
    yaml_config = YAMLConfig(config_file)
    yaml_config.dereference_all()
    with open(schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)
    # Collect and report on schema-validation errors.
    errors = _validation_errors(yaml_config.data, schema)
    log_method = log.error if errors else log.info
    log_method("%s schema-validation error%s found", len(errors), "" if len(errors) == 1 else "s")
    for error in errors:
        for line in str(error).split("\n"):
            log.error(line)
    # It's pointless to evaluate an invalid config, so return now if that's the case.
    if errors:
        return False
    # If no issues were detected, report success.
    return True


# Private functions


def _validation_errors(config: dict, schema: dict) -> List[str]:
    """
    Identify schema-validation errors.
    """
    validator = jsonschema.Draft202012Validator(schema)
    return list(validator.iter_errors(config))