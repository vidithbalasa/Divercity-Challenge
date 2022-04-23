from dataclasses import dataclass

@dataclass
class LinkedinProfile():
    first_name: str
    last_name: str
    location: str
    label: str
    profile_pic: str # stored as link to the source image

class LinkedinEmployees(list):
    def add_employee(self, first_name:str, last_name:str, /, *, location:str, label:str, profile_pic:str) -> None:
        self.append(LinkedinProfile(first_name, last_name, location, label, profile_pic))