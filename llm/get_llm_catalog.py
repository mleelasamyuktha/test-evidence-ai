from config.validation_catalog import VALIDATION_CATALOG

def get_llm_catalog():
    llm_catalog = {}

    for category, validations in VALIDATION_CATALOG.items():
        llm_catalog[category] = {}

        for validation_type, details in validations.items():
            llm_catalog[category][validation_type] = {
                "description": details["description"],
                "required_inputs": details["required_inputs"],
                "optional_inputs": details["optional_inputs"]
            }

    return llm_catalog


catalog = get_llm_catalog()
