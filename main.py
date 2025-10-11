import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from dataclasses import asdict


# GraphQL type definition for Movie
@strawberry.type
class Actor:
    id: int
    name: str
    movie_id: int


ACTORS = [
    Actor(id=1, name="Leonardo DiCaprio", movie_id=1),
    Actor(id=2, name="Joseph Gordon-Levitt", movie_id=1),
    Actor(id=3, name="Matthew McConaughey", movie_id=2),
    Actor(id=4, name="Anne Hathaway", movie_id=2),
]


# This describes the shape of movie data in our API.
@strawberry.type
class Movie:
    id: int
    title: str
    year: int
    rating: float

    @strawberry.field
    def actors(self) -> list[Actor]:
        return [a for a in ACTORS if a.movie_id == self.id]


# what the client sends to create a movie
@strawberry.input
class AddMovieInput:
    title: str
    year: int
    rating: float


# what the client sends to create a movie
@strawberry.type
class AddMoviePayload:
    ok: bool
    error: str | None
    movie: Movie | None


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


@strawberry.input
class DeleteMovieInput:
    id: int


@strawberry.type
class DeleteMoviePayload:
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
    def add_movie(self, input: AddMovieInput) -> AddMoviePayload:
        """Create a movie with basic validation and return a payload"""
        global NEXT_ID

        # basic validation
        if not input.title.strip():
            return AddMoviePayload(ok=False, error="Title cannot be empty", movie=None)
        if not (0.0 <= input.rating <= 5.0):
            return AddMoviePayload(ok=False, error="Rating must be between 0 and 5", movie=None)

        # create + store
        new_movie = Movie(id=NEXT_ID, title=input.title, year=input.year, rating=input.rating)
        MOVIES.append(new_movie)
        NEXT_ID += 1

        # structured response
        return AddMoviePayload(ok=True, error=None, movie=new_movie)

    @strawberry.field
    def delete_movie(self, input: DeleteMovieInput) -> DeleteMoviePayload:
        """Remove a movie by ID and return a structured payload"""
        for i, m in enumerate(MOVIES):
            if m.id == input.id:
                removed = MOVIES.pop(i)
                return DeleteMoviePayload(ok=True, error=None, movie=removed)
        # Not found
        return DeleteMoviePayload(ok=False, error="Movie not found", movie=None)

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

        # 3 - Apply only provided fields (generic and scalable)
        data = asdict(input)
        data.pop("id", None)
        for field_name, value in data.items():
            if value is not None:
                setattr(target, field_name, value)

        # 4 - Return structured result
        return UpdateMoviePayload(ok=True, error=None, movie=target)


# Create the GraphQL schema object
# This registers the Query type as the root for all queries.
# The schema ties together our type definitions (Movie) and resolvers (movies).
schema = strawberry.Schema(query=Query, mutation=Mutation)


app = FastAPI()

# Turn the schema into a GraphQL route
graphql_app = GraphQLRouter(schema)


# Mount the GraphQL route at /graphql
app.include_router(graphql_app, prefix="/graphql")

