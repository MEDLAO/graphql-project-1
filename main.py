import strawberry
from fastapi import FastAPI


@strawberry.type
class Movie:
    id: int
    title: str
    year: int
    rating: float