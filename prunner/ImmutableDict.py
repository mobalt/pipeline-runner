import logging
from collections import UserDict


class ImmutableDict(UserDict):
    def update(self, update_dict) -> None:
        for k, v in update_dict.items():
            if k in self:
                logging.warning(f"The variable ({k}) is already defined. Ignoring: {k} => {v}")
            else:
                self[k] = v
