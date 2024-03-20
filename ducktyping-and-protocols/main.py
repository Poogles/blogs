from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from typing import TypeVar, Protocol, reveal_type, runtime_checkable


@dataclass
class Person:
    id: UUID
    name: str


@dataclass
class Bug:
    id: UUID
    name: str


@dataclass
class Plant:
    id: UUID
    latin_name: str


@runtime_checkable
class Named(Protocol):
    name: str


T = TypeVar("T", bound=Named)


def record_visit(_object: T) -> tuple[T, str]:
    timecard = f"Visitor: {_object.name}, Time: {datetime.utcnow()}"
    return _object, timecard


def check_person(person: Person) -> None:
    pass


if __name__ == "__main__":
    woody = Person(id=uuid4(), name="Woody")
    visitor, timecard = record_visit(woody)
    check_person(visitor)

    chuckypig = Bug(id=uuid4(), name="Chucky")
    next_visitor, timecard = record_visit(chuckypig)
    # # main.py:52: error: Argument 1 to "check_person" has
    # #   incompatible type "Bug"; expected "Person"  [arg-type]
    # check_person(next_visitor)

    # oak_tree = Plant(id=uuid4(), latin_name="Quercus robur")
    # # main.py:57: error: Value of type variable "T" of "record_visit"
    # #   cannot be "Plant"  [type-var]
    # final_visitor, timecard = record_visit(oak_tree)
    # # main.py:60: error: Argument 1 to "check_person" has
    # #   incompatible type "Plant"; expected "Person"  [arg-type]
    # check_person(final_visitor)
