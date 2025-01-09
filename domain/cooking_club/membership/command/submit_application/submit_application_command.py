from dataclasses import dataclass
from common.command.command import Command

@dataclass
class SubmitApplicationCommand(Command):
    first_name: str
    last_name: str
    favorite_cuisine: str
    years_of_professional_experience: int
    number_of_cooking_books_read: int