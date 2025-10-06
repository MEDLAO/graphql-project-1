import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


# GraphQL type definition for Movie
# This describes the shape of movie data in our API.
@strawberry.type
class Movie:
    id: int
    title: str
    year: int
    rating: float


# GraphQL Query type
# Acts as the entry point for clients to fetch data.
# The "movies" field is a resolver function:
# - It returns a list of Movie objects (currently hardcoded for testing).
# - In a real app, this would fetch data from a database.
@strawberry.type
class Query:
    @strawberry.field
    def movies(self) -> list[Movie]:
        return [
            Movie(id=1, title="Inception", year=2010, rating=4.8),
            Movie(id=2, title="Interstellar", year=2014, rating=4.6)
        ]


# Create the GraphQL schema object
# This registers the Query type as the root for all queries.
# The schema ties together our type definitions (Movie) and resolvers (movies).
schema = strawberry.Schema(query=Query)


app = FastAPI()

# Turn the schema into a GraphQL route
graphql_app = GraphQLRouter(schema)


# Mount the GraphQL route at /graphql
app.include_router(graphql_app, prefix="/graphql")

