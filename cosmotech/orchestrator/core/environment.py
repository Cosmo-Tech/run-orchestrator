import os
from dataclasses import dataclass
from dataclasses import field
from dataclasses import field
from dataclasses import field
from dataclasses import field


@dataclass
class EnvironmentVariable:
    name: str = field()
    defaultValue: str = field(default=None)
    value: str = field(default=None)
    description: str = field(default=None)

    def is_required(self):
        return not self.value and not self.defaultValue

    def effective_value(self):
        v = self.value or os.environ.get(self.name, self.defaultValue)
        if v is not None:
            return str(v)
        return None

    def join(self, other: 'EnvironmentVariable'):
        self.defaultValue = self.defaultValue or other.defaultValue
        self.value = self.value or other.value
        self.description = self.description or other.description

    def serialize(self):
        r = {}
        if self.value:
            r['value'] = self.value
        if self.defaultValue:
            r['defaultValue'] = self.defaultValue
        if self.description:
            r['description'] = self.description
        return r
