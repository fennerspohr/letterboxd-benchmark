import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from pymongo import MongoClient, ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://admin:benchmark_local@localhost:27017/?authSource=admin",
)

client = MongoClient(MONGO_URI)
db = client["letterboxd"]
movies = db["movies"]


class MovieCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    date: Optional[int] = Field(default=None, ge=1800, le=2100)
    tagline: Optional[str] = None
    description: Optional[str] = None
    minute: Optional[int] = Field(default=None, ge=0)
    rating: Optional[float] = Field(default=None, ge=0, le=5)


class MovieUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=300)
    date: Optional[int] = Field(default=None, ge=1800, le=2100)
    tagline: Optional[str] = None
    description: Optional[str] = None
    minute: Optional[int] = Field(default=None, ge=0)
    rating: Optional[float] = Field(default=None, ge=0, le=5)


class MovieResponse(BaseModel):
    id: int
    name: str
    date: Optional[int] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    minute: Optional[int] = None
    rating: Optional[float] = None


def serialize_movie(movie: dict) -> dict:
    return {
        "id": movie["_id"],
        "name": movie["name"],
        "date": movie.get("date"),
        "tagline": movie.get("tagline"),
        "description": movie.get("description"),
        "minute": movie.get("minute"),
        "rating": movie.get("rating"),
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    client.admin.command("ping")

    # Inicializa o contador acima do maior ID já importado.
    max_movie = movies.find_one(sort=[("_id", -1)])
    initial_sequence = max_movie["_id"] if max_movie else 0

    db.counters.update_one(
        {"_id": "movie_id"},
        {"$max": {"sequence": initial_sequence}},
        upsert=True,
    )

    yield
    client.close()


app = FastAPI(
    title="Letterboxd Benchmark API",
    description="API CRUD de filmes para experimentos de desempenho.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    client.admin.command("ping")
    return {"status": "ok"}


@app.post(
    "/movies",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_movie(movie: MovieCreate):
    counter = db.counters.find_one_and_update(
        {"_id": "movie_id"},
        {"$inc": {"sequence": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    document = movie.model_dump()
    document["_id"] = counter["sequence"]

    try:
        movies.insert_one(document)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="ID de filme duplicado",
        )

    return serialize_movie(document)


@app.get("/movies", response_model=list[MovieResponse])
def list_movies(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=1000),
    year: Optional[int] = Query(default=None, ge=1800, le=2100),
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
):
    filters = {}

    if year is not None:
        filters["date"] = year

    if min_rating is not None:
        filters["rating"] = {"$gte": min_rating}

    cursor = movies.find(filters).skip(skip).limit(limit)
    return [serialize_movie(movie) for movie in cursor]


@app.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int):
    movie = movies.find_one({"_id": movie_id})

    if movie is None:
        raise HTTPException(
            status_code=404,
            detail="Filme não encontrado",
        )

    return serialize_movie(movie)


@app.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(movie_id: int, update: MovieUpdate):
    changes = update.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="Nenhum campo informado",
        )

    result = movies.update_one(
        {"_id": movie_id},
        {"$set": changes},
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Filme não encontrado",
        )

    return serialize_movie(movies.find_one({"_id": movie_id}))


@app.delete(
    "/movies/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_movie(movie_id: int):
    result = movies.delete_one({"_id": movie_id})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Filme não encontrado",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/admin/indexes")
def create_year_index():
    name = movies.create_index([("date", ASCENDING)])
    return {"created_index": name}


@app.delete("/admin/indexes/year")
def remove_year_index():
    try:
        movies.drop_index("date_1")
    except Exception as error:
        if "index not found" not in str(error).lower():
            raise HTTPException(status_code=400, detail=str(error))

    return {"status": "year index removed if it existed"}