import strawberry
from dataclasses import asdict
from auth.utils import require_login


@strawberry.input
class LoginInput:
    """Shape of the data the client sends for login."""
    email: str
    password: str


@strawberry.type
class LoginPayload:
    """Shape of the data returned by the login mutation."""
    ok: bool  # True if login succeeded
    error: str | None = None  # Error message when login fails (None on success)


# GraphQL type definition for Actor and Movie
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


@strawberry.input
class AddActorInput:
    name: str
    movie_id: int


@strawberry.type
class AddActorPayload:
    name: str
    movie_id: int


@strawberry.input
class UpdateActorInput:
    id: int
    name: str | None = None
    movie_id: int | None = None


@strawberry.type
class UpdateActorPayload:
    ok: bool
    error: str | None
    actor: Actor | None


@strawberry.input
class DeleteActorInput:
    id: int


@strawberry.type
class DeleteActorPayload:
    ok: bool
    error: str | None
    actor: Actor | None


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
    def actors(self) -> list[Actor]:
        return ACTORS

    @strawberry.field
    def movie(self, id: int) -> Movie | None:
        """Fetch a single movie by its ID"""
        for m in MOVIES:
            if m.id == id:
                return m
        return None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_actor(self, info, input: AddActorInput) -> Actor:
        """Create a new actor and link it to a movie"""
        require_login(info)
        new_id = max((a.id for a in ACTORS), default=0) + 1
        new_actor = Actor(id=new_id, name=input.name, movie_id=input.movie_id)
        ACTORS.append(new_actor)
        return new_actor

    @strawberry.mutation
    def delete_actor(self, info, input: DeleteActorInput) -> DeleteActorPayload:
        require_login(info)
        for i, a in enumerate(ACTORS):
            if a.id == input.id:
                removed = ACTORS.pop(i)
                return DeleteActorPayload(ok=True, error=None, actor=removed)
        return DeleteActorPayload(ok=False, error="Actor not found", actor=None)

    @strawberry.mutation
    def update_actor(self, info, input: UpdateActorInput) -> UpdateActorPayload:
        """Partially update an actor and return status + updated object"""
        require_login(info)
        # 1 - Find the actor by id
        target = next((a for a in ACTORS if a.id == input.id), None)
        if target is None:
            return UpdateActorPayload(ok=False, error="Actor not found", actor=None)

        # 2 - Apply only provided fields
        data = asdict(input)
        data.pop("id", None)
        for field_name, value in data.items():
            if value is not None:
                setattr(target, field_name, value)

        # 3 - Return structured result
        return UpdateActorPayload(ok=True, error=None, actor=target)

    @strawberry.mutation
    def add_movie(self, info, input: AddMovieInput) -> AddMoviePayload:
        """Create a movie with basic validation and return a payload"""
        require_login(info)
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

    @strawberry.mutation
    def delete_movie(self, info, input: DeleteMovieInput) -> DeleteMoviePayload:
        """Remove a movie by ID and return a structured payload"""
        require_login(info)
        for i, m in enumerate(MOVIES):
            if m.id == input.id:
                removed = MOVIES.pop(i)
                return DeleteMoviePayload(ok=True, error=None, movie=removed)
        # Not found
        return DeleteMoviePayload(ok=False, error="Movie not found", movie=None)

    @strawberry.mutation
    def update_movie(self, info, input: UpdateMovieInput) -> UpdateMoviePayload:
        """Partially update a movie and return status + updated object"""
        require_login(info)
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

