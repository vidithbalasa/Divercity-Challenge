from dataclasses import dataclass

@dataclass
class LinkedinProfile:
    first_name: str
    last_name: str
    location: str
    label: str
    profile_pic: str # stored as link to the source image

class Employees(list):
    # self: list[LinkedinProfile]
    def add_employee(self, first_name:str, last_name:str, *, location:str, label:str, profile_pic:str) -> None:
        self.append(LinkedinProfile(first_name, last_name, location, label, profile_pic))
    
    def save_as_csv(self, file_name: str):
        with open(file_name, 'w') as f:
            f.write('first_name,last_name,location,label,profile_pic\n')
            for employee in self:
                f.write(f'{employee.first_name.strip()},{employee.last_name.strip()},{employee.location.strip()},{employee.label.strip()},{employee.profile_pic.strip()}\n')