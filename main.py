import strawberry
from fastapi import FastAPI


@strawberry.type
class Movie:
    id: int
    title: str
    year: int
    rating: float


@strawberry.type
class Query:
    @strawberry.field
    def movies(self) -> list[Movie]:
        return [
            Movie(id=1, title="Inception", year=2010, rating=4.8),
            Movie(id=2, title="Interstellar", year=2014, rating=4.6)
        ]


schema = strawberry.Schema(query=Query)