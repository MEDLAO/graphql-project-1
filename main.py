import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from dataclasses import asdict


# GraphQL type definition for Movie
# This describes the shape of movie data in our API.
@strawberry.type
class Movie:
    id: int
    title: str
    year: int
    rating: float


# GraphQL input object (for arguments)
@strawberry.input
class UpdateMovieInput:
    id: int
    title: str | None = None
    year: int | None = None
    rating: float | None = None


# normal GraphQL object (response shape)
@strawberry.type
class UpdateMoviePayload:
    ok: bool
    error: str | None
    movie: Movie | None


MOVIES = [
    Movie(id=1, title="Inception", year=2010, rating=4.8),
    Movie(id=2, title="Interstellar", year=2014, rating=4.6),
]
# ID counter for new movies
NEXT_ID = 3


# GraphQL Query type
# Acts as the entry point for clients to fetch data.
# The "movies" field is a resolver function:
# - It returns a list of Movie objects (currently hardcoded for testing).
# - In a real app, this would fetch data from a database.
@strawberry.type
class Query:
    @strawberry.field
    def movies(self) -> list[Movie]:
        return MOVIES

    @strawberry.field
    def movie(self, id: int) -> Movie | None:
        """Fetch a single movie by its ID"""
        for m in MOVIES:
            if m.id == id:
                return m
        return None


@strawberry.type
class Mutation:
    @strawberry.field
    def add_movie(self, title: str, year: int, rating: float) -> Movie:
        """Create a new movie and return it"""
        global NEXT_ID
        new_movie = Movie(id=NEXT_ID, title=title, year=year, rating=rating)
        MOVIES.append(new_movie)
        NEXT_ID += 1
        return new_movie

    @strawberry.field
    def delete_movie(self, id: int) -> Movie | None:
        """Remove a movie by ID and return the deleted movie (or None if not found)"""
        for i, m in enumerate(MOVIES):
            if m.id == id:
                return MOVIES.pop(i)
        return None

    @strawberry.field
    def update_movie(self, input: UpdateMovieInput) -> UpdateMoviePayload:
        """Partially update a movie and return status + updated object"""

        # 1 - Find the movie by id (first match or None)
        target = next((m for m in MOVIES if m.id == input.id), None)
        if target is None:
            return UpdateMoviePayload(ok=False, error="Rating must be between 0 and 5", movie=None)

        # 2 - Validate inputs
        if input.rating is not None and not (0.0 <= input.rating <= 5.0):
            return UpdateMoviePayload(ok=False, error="Rating must be between 0 and 5", movie=None)


# Create the GraphQL schema object
# This registers the Query type as the root for all queries.
# The schema ties together our type definitions (Movie) and resolvers (movies).
schema = strawberry.Schema(query=Query, mutation=Mutation)


app = FastAPI()

# Turn the schema into a GraphQL route
graphql_app = GraphQLRouter(schema)


# Mount the GraphQL route at /graphql
app.include_router(graphql_app, prefix="/graphql")

