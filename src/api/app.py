from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
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
    image_url: Optional[str]
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
async def search_recipes(
    name: str | None = None,
    ingredient: str | None = None,
    include_ingredients: str | None = None,
    exclude_ingredients: str | None = None,
) -> list[RecipeResponse]:
    recipes = []
    # If no search criteria provided, return empty list
    if not any([name, ingredient, include_ingredients]):
        return []

    if name:
        recipes.extend(api_service.search_recipes_by_name(name))
    if ingredient:
        recipes.extend(api_service.search_recipes_by_ingredient(ingredient))
    # If only include_ingredients is provided, get recipes from both sources
    elif include_ingredients:
        # Get recipes from database
        recipes.extend(db.get_all_recipes())
        # Get recipes from API for each included ingredient
        for ing in include_ingredients.split(","):
            recipes.extend(api_service.search_recipes_by_ingredient(ing.strip()))

    def extract_ingredient_name(ingredient_str: str) -> str:
        # Remove measurements and units (e.g., "100g Flour" -> "Flour")
        # Split by space and take the last word(s) that form the ingredient name
        parts = ingredient_str.split()
        # Find the first word that doesn't look like a measurement or unit
        for i, part in enumerate(parts):
            if not any(c.isdigit() for c in part) and part.lower() not in [
                "g",
                "ml",
                "tbsp",
                "tsp",
                "tbls",
                "to",
                "serve",
            ]:
                return " ".join(parts[i:])
        return ingredient_str

    # Filter recipes based on include/exclude ingredients
    if include_ingredients:
        include_list = [i.strip().lower() for i in include_ingredients.split(",")]
        recipes = [
            r
            for r in recipes
            if any(
                any(include_ing in extract_ingredient_name(ing).lower() for ing in r.ingredients)
                for include_ing in include_list
            )
        ]

    if exclude_ingredients:
        exclude_list = [i.strip().lower() for i in exclude_ingredients.split(",")]
        recipes = [
            r
            for r in recipes
            if not any(
                any(exclude_ing in extract_ingredient_name(ing).lower() for ing in r.ingredients)
                for exclude_ing in exclude_list
            )
        ]

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
        is_custom=recipe.is_custom,
    )
    db.add_recipe(custom_recipe)
    return RecipeResponse(**custom_recipe.to_dict())


# A random recipe from the list of favorites 
@app.get("/recipes/random_from_favorites")
def get_random_favorite_recipe(user_id: str):

    favorite_recipes = db.get_favorite_recipes(user_id)
    if not favorite_recipes:
        return {"error": "No favorite recipes found."}

    random_recipe = random.choice(favorite_recipes)
    return random_recipe


# Random recipe from the custom list 
@app.get("/recipes/random_from_custom")
def get_random_custom_recipe(user_id: str):

    custom_recipes = db.get_custom_recipes(user_id)
    if not custom_recipes:
        return {"error": "No custom recipes found."}

    random_recipe = random.choice(custom_recipes)
    return random_recipe
