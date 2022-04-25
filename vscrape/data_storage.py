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
    
    def save_as_csv(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            f.write('first_name,last_name,location,label,profile_pic\n')
            for employee in self:
                f.write(f'{employee.first_name.strip()},{employee.last_name.strip()},{employee.location.strip()},{employee.label.strip()},{employee.profile_pic.strip()}\n')
    
    # # change the append function so that it updates the loading bar each time
    # def append(self, employee: LinkedinProfile) -> None:
    #     super().append(employee)
    #     # loading bar
    #     print(f'\r{self.__len__()}/{len(self)}', end='\r')
    
    def __repr__(self) -> str:
        s = ''
        for employee in self[:5]:
            s += f'{employee.first_name.strip()} {employee.last_name.strip()} ({employee.location.strip()}) :: {employee.label.strip()}\n'
        if self.__len__() > 5:
            s += f'...\n'
        return s 