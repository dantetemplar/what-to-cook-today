from unittest.mock import Mock, patch

import pytest

from src.models.recipe import Recipe
from src.services.api_service import APIService


@pytest.fixture
def api_service():
    return APIService()


@pytest.fixture
def mock_meal_data():
    return {
        "meals": [
            {
                "idMeal": "123",
                "strMeal": "Test Meal",
                "strMealThumb": "http://example.com/image.jpg",
                "strInstructions": "Test instructions",
                "strIngredient1": "ingredient1",
                "strMeasure1": "1 cup",
                "strIngredient2": "ingredient2",
                "strMeasure2": "2 tbsp",
            }
        ]
    }


def test_get_random_recipe_success(api_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "meals": [
            {
                "idMeal": "123",
                "strMeal": "Test Recipe",
                "strMealThumb": "http://example.com/image.jpg",
                "strInstructions": "Test instructions",
                "strIngredient1": "ingredient1",
                "strIngredient2": "ingredient2",
                "strMeasure1": "measure1",
                "strMeasure2": "measure2",
            }
        ]
    }

    with patch.object(api_service.session, "get", return_value=mock_response):
        recipe = api_service.get_random_recipe()
        assert isinstance(recipe, Recipe)
        assert recipe.id == "123"
        assert recipe.name == "Test Recipe"
        assert recipe.image_url == "http://example.com/image.jpg"
        assert recipe.instructions == "Test instructions"
        assert len(recipe.ingredients) == 2


def test_get_random_recipe_no_meals(api_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"meals": None}

    with patch.object(api_service.session, "get", return_value=mock_response):
        recipe = api_service.get_random_recipe()
        assert recipe is None


def test_get_random_recipe_error(api_service):
    with patch.object(api_service.session, "get", side_effect=Exception("API Error")):
        recipe = api_service.get_random_recipe()
        assert recipe is None


def test_search_recipes_by_name(api_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "meals": [
            {
                "idMeal": "123",
                "strMeal": "Test Recipe",
                "strMealThumb": "http://example.com/image.jpg",
                "strInstructions": "Test instructions",
                "strIngredient1": "ingredient1",
                "strIngredient2": "ingredient2",
                "strMeasure1": "measure1",
                "strMeasure2": "measure2",
            }
        ]
    }

    with patch.object(api_service.session, "get", return_value=mock_response):
        recipes = api_service.search_recipes_by_name("test")
        assert len(recipes) == 1
        assert isinstance(recipes[0], Recipe)
        assert recipes[0].id == "123"


def test_search_recipes_by_ingredient(api_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "meals": [
            {
                "idMeal": "123",
                "strMeal": "Test Recipe",
                "strMealThumb": "http://example.com/image.jpg",
                "strInstructions": "Test instructions",
                "strIngredient1": "ingredient1",
                "strIngredient2": "ingredient2",
                "strMeasure1": "measure1",
                "strMeasure2": "measure2",
            }
        ]
    }

    with patch.object(api_service.session, "get", return_value=mock_response):
        recipes = api_service.search_recipes_by_ingredient("ingredient1")
        assert len(recipes) == 1
        assert isinstance(recipes[0], Recipe)
        assert recipes[0].id == "123"


def test_parse_meal_to_recipe(api_service):
    meal_data = {
        "idMeal": "123",
        "strMeal": "Test Recipe",
        "strMealThumb": "http://example.com/image.jpg",
        "strInstructions": "Test instructions",
        "strIngredient1": "ingredient1",
        "strIngredient2": "ingredient2",
        "strMeasure1": "measure1",
        "strMeasure2": "measure2",
    }

    recipe = api_service._parse_meal_to_recipe(meal_data)
    assert isinstance(recipe, Recipe)
    assert recipe.id == "123"
    assert recipe.name == "Test Recipe"
    assert recipe.image_url == "http://example.com/image.jpg"
    assert recipe.instructions == "Test instructions"
    assert len(recipe.ingredients) == 2


def test_search_recipes_by_name_success(api_service):
    mock_response = {
        "meals": [
            {
                "idMeal": "777",
                "strMeal": "My super recipe",
                "strMealThumb": "http://example.com/image.jpg",
                "strInstructions": "Test instructions",
                "strIngredient1": "Chicken",
                "strMeasure1": "200g",
                "strIngredient2": "Protein",
                "strMeasure2": "1 tsp",
                "strIngredient3": None,
                "strMeasure3": None,
            }
        ]
    }

    with patch.object(api_service.session, "get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Call the method
        recipes = api_service.search_recipes_by_name("Test")

        # Assertions
        assert len(recipes) == 1
        recipe = recipes[0]
        assert isinstance(recipe, Recipe)
        assert recipe.id == "777"
        assert recipe.name == "My super recipe"
        assert recipe.image_url == "http://example.com/image.jpg"
        assert recipe.instructions == "Test instructions"
        assert recipe.ingredients == ["200g Chicken", "1 tsp Protein"]