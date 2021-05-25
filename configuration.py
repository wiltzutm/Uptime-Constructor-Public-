import dataclasses
import json
from typing import List


@dataclasses.dataclass
class Device:
    _id: str
    ip: str
    locations: List[str]

    @property
    def uid(self):
        return f"{self.name}-{self.ip}"


@dataclasses.dataclass
class Person:
    _id: str
    name: str
    email: str
    title: str = ""
    company: str = ""


@dataclasses.dataclass
class InputSettings:
    _id: str
    format: str
    folder: str

    @property
    def fullpath(self):
        return pathlib.Path(self.folder + "/" + self.format)


class OutputSettings(InputSettings):
    pass


@dataclasses.dataclass
class Project:
    name: str
    contract: str
    contacts: List[str]
    maintainers: List[str]
    devices_in_use: List[str]


@dataclasses.dataclass
class BaseConfiguration:
    all_company_contacts: List[Person]
    all_maintainers: List[Person]
    devices: List[Device]
    projects: List[Project]
    input_settings: List[InputSettings]
    output_settings: List[OutputSettings]


# def person_json_to_dict(js):
#     result = {}
#     result["_id"] = js.get("id", None)
#     for name in ["name", "title", "company", "email"]:
#         result[name] = js.get(name, None)
#     return result

def clean_id_json_to_dict(js):
    result = {} 
    result["_id"] = js.get("id", None)
    attrs = set(js.keys())
    attrs.remove('id')
    for name in attrs:
        result[name] = js.get(name, None)
    return result


# def input_setting_json_to_dict(js):
#     result = {}
#     result["_id"] = js.get("id", None)
#     for name in js.keys():
#         result[name] = js.get(name, None)
#     return result

def _parse_devices(json_data) -> List[Device]:
    devices = []
    for data in json_data["devices"]:
        dev = Device(data.get('id', None), data.get("ip", None), [loc for loc in data["locations"]])
        devices.append(dev)
    return devices


def _parse_contacts(json_data):
    contacts = []
    for cdata in json_data["contacts"]:
        contact = Person(**clean_id_json_to_dict(cdata))
        contacts.append(contact)
    return contacts


def _parse_maintainers(json_data):
    maintainers = []
    for mdata in json_data["maintainers"]:
        pe = Person(**clean_id_json_to_dict(mdata))
        maintainers.append(pe)
    return maintainers


def _parse_projects(json_data):
    projects = []
    for pdata in json_data["projects"]:
        projects.append(Project(**pdata))
    return projects


def _parse_input_settings(json_data) -> List[InputSettings]:
    return [InputSettings(**clean_id_json_to_dict(idata)) for idata in json_data["inputsettings"]]


def _parse_output_settings(json_data) -> List[OutputSettings]:
    return [OutputSettings(**clean_id_json_to_dict(idata)) for idata in json_data["outputsettings"]]

def validate_id_exists(all_objects, used_ids):
    erroneous_cases = []
    for uid in used_ids:
        was_in = False
        for obj in all_objects:
            if uid == obj._id:
                was_in = True
                break
        if not was_in:
            erroneous_cases.append(uid)
    if erroneous_cases:
        raise ValueError(f"Cannot find definition of used ids: {erroneous_cases} in config file.") 


def parse_config_json(filepath) -> BaseConfiguration:
    f = open(filepath, 'r')
    json_data = json.loads(f.read())
    f.close()
    all_devices = _parse_devices(json_data)
    all_contacts = _parse_contacts(json_data)
    all_maintainers = _parse_maintainers(json_data)
    all_projects = _parse_projects(json_data)
    all_input_settings = _parse_input_settings(json_data)
    all_output_settings = _parse_output_settings(json_data)
    # Do some light validation:
    for project in all_projects:
        validate_id_exists(all_contacts, project.contacts)
        validate_id_exists(all_maintainers, project.maintainers)
        validate_id_exists(all_devices, project.devices_in_use)
    return BaseConfiguration(all_contacts, all_maintainers, all_devices, all_projects, all_input_settings, all_output_settings)


CONFIG = parse_config_json("devicesexample.json")
# json.loads(open("appsettings.json").read())
