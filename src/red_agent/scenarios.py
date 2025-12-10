from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    difficulty_levels: List[str]


SCENARIOS: List[Scenario] = [
    Scenario(
        name="salary_slip",
        description="Victim is asked to download a 'revised salary slip' from a link.",
        difficulty_levels=["easy", "medium", "hard"],
    ),
    Scenario(
        name="it_support",
        description="IT desk requests password reset verification.",
        difficulty_levels=["easy", "medium"],
    ),
    Scenario(
        name="account_verification",
        description="Security team claims unusual login and asks for confirmation.",
        difficulty_levels=["easy", "medium", "hard"],
    ),
     Scenario(
        name="Aadhar_verification",
        description="As per government policy Aadhar verification for all citizens once a year is compulsary.",
        difficulty_levels=["easy", "medium", "hard"],
    ),
]
