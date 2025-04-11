import requests

from ..models.recipe import Recipe


class APIService:
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"

    def __init__(self):
        self.session = requests.Session()

    def get_random_recipe(self) -> Recipe | None:
        try:
            response = self.session.get(f"{self.BASE_URL}/random.php")
            if response.status_code == 200:
                data = response.json()
                if data["meals"]:
                    meal = data["meals"][0]
                    return self._parse_meal_to_recipe(meal)
            return None
        except Exception:
            return None

    def search_recipes_by_name(self, name: str) -> list[Recipe]:
        try:
            response = self.session.get(f"{self.BASE_URL}/search.php?s={name}")
            if response.status_code == 200:
                data = response.json()
                if data["meals"]:
                    return [self._parse_meal_to_recipe(meal) for meal in data["meals"]]
            return []
        except Exception:
            return []

    def search_recipes_by_ingredient(self, ingredient: str) -> list[Recipe]:
        try:
            response = self.session.get(f"{self.BASE_URL}/filter.php?i={ingredient}")
            if response.status_code == 200:
                data = response.json()
                if data["meals"]:
                    return [self._parse_meal_to_recipe(meal) for meal in data["meals"]]
            return []
        except Exception:
            return []

    def _parse_meal_to_recipe(self, meal: dict) -> Recipe:
        ingredients = []
        for i in range(1, 21):  # TheMealDB has up to 20 ingredients
            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ingredient and ingredient.strip():
                ingredients.append(f"{measure.strip()} {ingredient.strip()}" if measure else ingredient.strip())

        return Recipe(
            id=meal["idMeal"],
            name=meal["strMeal"],
            image_url=meal["strMealThumb"],
            instructions=meal["strInstructions"],
            ingredients=ingredients,
        )
