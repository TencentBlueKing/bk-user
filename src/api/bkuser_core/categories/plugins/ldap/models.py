from dataclasses import dataclass
from typing import List, Optional

from django.utils.functional import cached_property


@dataclass
class UserProfile:
    username: str
    display_name: str
    email: str
    telephone: str
    code: str

    departments: List[List[str]]

    @property
    def key_field(self):
        return self.username

    @property
    def display_str(self):
        return self.display_name


@dataclass
class DepartmentProfile:
    name: str
    parent: Optional['DepartmentProfile'] = None
    code: Optional[str] = None
    is_group: bool = False

    @property
    def key_field(self):
        return self.display_str

    @cached_property
    def display_str(self):
        if self.parent:
            return self.parent.display_str + "/" + self.name
        return self.name
