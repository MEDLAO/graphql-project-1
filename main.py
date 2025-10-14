from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from graphql.schema import schema


app = FastAPI()

# Turn the schema into a GraphQL route
graphql_app = GraphQLRouter(schema)


# Mount the GraphQL route at /graphql
app.include_router(graphql_app, prefix="/graphql")
