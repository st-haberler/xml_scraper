from dataclasses import fields, is_dataclass


def source_from_ecli(ecli: str) -> str:
    # example: ECLI:AT:VFGH:2022:E1273.2019
    return ecli.split(":")[2].lower()


def from_dict(dataclass_type, data):
    if not is_dataclass(dataclass_type):
        raise ValueError(f"{dataclass_type} is not a dataclass")

    # Get the fields of the dataclass
    dataclass_fields = fields(dataclass_type)

    # Initialize an empty dictionary to store the field values
    field_values = {}

    # Iterate over each field
    for field in dataclass_fields:
        field_name = field.name
        field_type = field.type

        print(field_name, field_type)

        # Check if the field is a nested dataclass
        if is_dataclass(field_type):
            # Recursively call from_dict for nested dataclasses
            nested_data = data.get(field_name)
            nested_instance = from_dict(field_type, nested_data)
            field_values[field_name] = nested_instance
        elif (
            getattr(field_type, "__origin__", None) == list
            and is_dataclass(field_type.__args__[0])
        ):
            # Handle List of dataclasses
            list_data = data.get(field_name, [])
            list_instances = [from_dict(field_type.__args__[0], item) for item in list_data]
            field_values[field_name] = list_instances
        else:
            # Use the value from the dictionary if present, or use the default value
            print("else: field_name", field_name)
            field_values[field_name] = data.get(field_name)

    # Create an instance of the dataclass using dataclasses.replace
    return dataclass_type(**field_values)
