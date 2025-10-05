
import pydantic
from pydantic import Field
import enum
import typing as T

EVENT_TYPES = ["investments", "education", "financial", "family", "health", "friends", 'love', 'lifestyle', "career"]

DEFAULT_DATE = "2022-01-30"

DEFAULT_HISTORY = [
    {"date": "2000-04-15", "title": "Born in Katowice"},
    {"date": "2018-06-20", "title": "Graduated from high school"},
    {"date": "2022-05-15", "title": "Graduated from university with a degree in Computer Science"},
    # {"date": "2023-09-01", "title": "Started first job as a Junior Developer at TechCorp"},
    # {"date": "2026-03-10", "title": "Promoted to Software Engineer at TechCorp"},
    # {"date": "2028-07-22", "title": "Moved to Kraków for a new job at Innovatech"},
    # {"date": "2030-11-30", "title": "Started freelancing as a web developer"},
    # {"date": "2032-01-15", "title": "Launched personal blog about tech and programming"},
    # {"date": "2070-04-15", "title": "Celebrated 80th birthday with friends and family"},
]
DEFAULT_HISTORY_AGNIESZKA = [
    {"date": "1996-08-12", "title": "Born in Warsaw"},
    {"date": "2015-05-25", "title": "Graduated from high school"},
    {"date": "2019-06-30", "title": "Graduated from university with a degree in Economics"},
    {"date": "2020-10-01", "title": "Started first job as a Junior Financial Analyst at FinServe"},
    {"date": "2021-04-15", "title": "Promoted to Financial Analyst at FinServe"},
    {"date": "2021-12-31", "title": "Meet Michał at a friend's wedding"},
    {"date": "2022-01-14", "title": "Started dating Michał"},
]
DEFAULT_PLAYER_AGNIESZKA = {
    "name": "Agnieszka",
    "gender": "female",
    "age": 25,  
    "health_level": {"value": 85, "unit": "of 100"},
    "energy_level": {"value": 75, "unit": "of 100"},
    "birth_date": "1996-08-12",
    "hometown": "Warsaw",
    "current_city": "Warsaw",
    "hobbies": ["reading", "traveling"],
    "marital_status": "dating",
    "skills": ["data analysis", "financial modeling"],
    "savings": {
        "cash": 15_000,
        "bank_account": 30_000,
        "retirement_account": 0
    },
    "current_job": "Financial Analyst at FinServe",
    "monthly_income": {
        "employment_contract": 6_000,
    },
    "monthly_outcome": {
        "rent": 2_500,
        "food": 1_200,
        "utilities": 400,
        "transportation": 200,
        "entertainment": 300,
    },
    "investments": {
        "shares": 0,
        "bonds": 0,
        "crypto": 0,
        "real_estate": 0,
    }
}

DEFAULT_PLAYER = {    
    "name": "Andrzej",
    "gender": "male",
    "age": 90,

    # "body_weight": {"value": 75, "unit": "kg"},
    "health_level": {"value": 70, "unit": "of 100"},
    "energy_level": {"value": 80, "unit": "of 100"},

    "birth_date": "2000-04-15",
    "hometown": "Katowice",
    
    "current_city": "Kraków",
    "hobbies": ["bieganie"],
    
    # family 
    "marital_status": "single",
    # "family_members": [],

    # knowledge
    "skills": ["programowanie w pythonie", "wygrywanie hackathonów"],

    # money
    "savings": {
        "cash": 500,
        "bank_account": 3_000,
        "retirement_account": 0
    },
    "monthly_income": {
        "employment_contract": 2_500,
        "allowance": 1_000
    },
    "monthly_outcome": {
        "rent": 2_000,
        "food": 500,
        "utilities": 500,
        "transportation": 300,
        "entertainment": 400,
    },
    "investments": {
        "shares": 0,
        "bonds": 0,
        "crypto": 1000,
        "real_estate": 0,
    },
}

UserParameter = enum.StrEnum('UserParameter', list(DEFAULT_PLAYER.keys()))

class Impact(pydantic.BaseModel):  
    parameter: UserParameter
    operation: enum.StrEnum("Operation", ["set", "add", "sub"])
    key: T.Optional[str] = Field(None, description="For dict parameters, the key to modify")
    value: T.Union[str,int, list]


# class ImpactsList(pydantic.BaseModel):
#     impacts: list[Impact]


class Event(pydantic.BaseModel):
    material_icon: str
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD
    title: str
    short_description: str
    player_impact: list[Impact]


class EventsList(pydantic.BaseModel):
    events: list[Event]


class HistorySummary(pydantic.BaseModel):
    summary: str = Field(..., description="A concise summary of the user's history in Polish.")
    quote: str = Field(None, description="A relevant quote that encapsulates the user's life story.")


class Reaction(pydantic.BaseModel):
    description: str = Field(..., description="A brief description of the reaction option.")
    # consequence_description: str = Field(..., description="A brief description of the final consequence of choosing this option.")
    player_impact: list[Impact]
    # your_life_impact: str = Field(..., description="One sentence description of how this reaction will impact the user's life.")
    

class PlayerReaction(pydantic.BaseModel):
    material_icon: str
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD
    title: str
    short_description: str
    reactions: list[Reaction]


class Action(pydantic.BaseModel):
    short_description: str
    player_impact: list[Impact]


class PlayerAction(pydantic.BaseModel):
    material_icon: str
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD
    actions: list[Action]