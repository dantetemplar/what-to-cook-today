from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from ..db.database import Database
from ..models.recipe import Recipe
from ..services.api_service import APIService

app = FastAPI(title="What to Cook Today API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
api_service = APIService()
db = Database()


class RecipeResponse(BaseModel):
    id: str
    name: str
    image_url: str
    instructions: str
    ingredients: list[str]
    is_favorite: bool
    is_custom: bool


class FavoriteRequest(BaseModel):
    user_id: str


@app.get("/recipes/random", response_model=RecipeResponse)
async def get_random_recipe() -> RecipeResponse:
    recipe = api_service.get_random_recipe()
    if not recipe:
        raise HTTPException(status_code=404, detail="No recipe found")
    db.add_recipe(recipe)
    return RecipeResponse(**recipe.to_dict())


@app.get("/recipes/search", response_model=list[RecipeResponse])
async def search_recipes(name: str | None = None, ingredient: str | None = None) -> list[RecipeResponse]:
    recipes = []
    if name:
        recipes.extend(api_service.search_recipes_by_name(name))
    if ingredient:
        recipes.extend(api_service.search_recipes_by_ingredient(ingredient))

    # Save recipes to database
    for recipe in recipes:
        db.add_recipe(recipe)

    return [RecipeResponse(**recipe.to_dict()) for recipe in recipes]


@app.get("/recipes/favorites", response_model=list[RecipeResponse])
async def get_favorite_recipes(user_id: str) -> list[RecipeResponse]:
    recipes = db.get_favorite_recipes(user_id)
    return [RecipeResponse(**recipe.to_dict()) for recipe in recipes]


@app.get("/recipes/custom", response_model=list[RecipeResponse])
async def get_custom_recipes() -> list[RecipeResponse]:
    recipes = db.get_custom_recipes()
    return [RecipeResponse(**recipe.to_dict()) for recipe in recipes]


@app.post("/recipes/{recipe_id}/favorite")
async def toggle_favorite(recipe_id: str, request: FavoriteRequest) -> dict:
    success = db.toggle_favorite(recipe_id, request.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"status": "success"}


@app.post("/recipes/custom", response_model=RecipeResponse)
async def add_custom_recipe(recipe: RecipeResponse) -> RecipeResponse:
    custom_recipe = Recipe(
        id=recipe.id,
        name=recipe.name,
        image_url=recipe.image_url,
        instructions=recipe.instructions,
        ingredients=recipe.ingredients,
        is_custom=True,
    )
    db.add_recipe(custom_recipe)
    return RecipeResponse(**custom_recipe.to_dict())
