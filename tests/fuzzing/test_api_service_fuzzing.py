from unittest.mock import Mock, patch

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.models.recipe import Recipe
from src.services.api_service import APIService

# Define strategies for API responses with safe characters
meal_strategy = st.fixed_dictionaries({
    "idMeal": st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"), min_size=1, max_size=10),
    "strMeal": st.text(min_size=1, max_size=100),
    "strMealThumb": st.text(min_size=1, max_size=200),
    "strInstructions": st.text(min_size=1, max_size=1000),
    **{f"strIngredient{i}": st.one_of(st.text(), st.none()) for i in range(1, 21)},
    **{f"strMeasure{i}": st.one_of(st.text(), st.none()) for i in range(1, 21)},
})

# Fixed: use proper strategy for empty list
empty_list_strategy = st.just([])

api_response_strategy = st.one_of(
    st.fixed_dictionaries({"meals": st.lists(meal_strategy, min_size=1)}),
    st.fixed_dictionaries({"meals": st.none()}),
    st.fixed_dictionaries({"meals": empty_list_strategy})
)

# New: Error response strategy for testing exception handling
error_strategy = st.one_of(
    st.just(Exception("Network error")),
    st.just(TimeoutError("Request timed out")),
    st.just(ValueError("Invalid response format"))
)


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(meal=meal_strategy)
def test_parse_meal_to_recipe_fuzzing(meal):
    """Test parsing of meal data to Recipe object with fuzzed inputs"""
    service = APIService()
    recipe = service._parse_meal_to_recipe(meal)
    
    assert isinstance(recipe, Recipe)
    assert recipe.id == meal["idMeal"]
    assert recipe.name == meal["strMeal"]
    assert recipe.image_url == meal["strMealThumb"]
    assert recipe.instructions == meal["strInstructions"]
    assert isinstance(recipe.ingredients, list)


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    search_term=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_ "), min_size=1, max_size=50),
    api_response=api_response_strategy
)
def test_search_recipes_by_name_fuzzing(search_term, api_response):
    """Test recipe search by name with fuzzed inputs"""
    with patch("requests.Session.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response
        mock_get.return_value = mock_response

        service = APIService()
        recipes = service.search_recipes_by_name(search_term)

        assert isinstance(recipes, list)
        if api_response["meals"]:
            assert len(recipes) == len(api_response["meals"])
            for recipe in recipes:
                assert isinstance(recipe, Recipe)
        else:
            assert len(recipes) == 0


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    ingredient=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_ "), min_size=1, max_size=50),
    api_response=api_response_strategy
)
def test_search_recipes_by_ingredient_fuzzing(ingredient, api_response):
    """Test recipe search by ingredient with fuzzed inputs"""
    with patch("requests.Session.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response
        mock_get.return_value = mock_response

        service = APIService()
        recipes = service.search_recipes_by_ingredient(ingredient)

        assert isinstance(recipes, list)
        if api_response["meals"]:
            assert len(recipes) == len(api_response["meals"])
            for recipe in recipes:
                assert isinstance(recipe, Recipe)
        else:
            assert len(recipes) == 0


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(api_response=api_response_strategy)
def test_get_random_recipe_fuzzing(api_response):
    """Test getting random recipe with fuzzed inputs"""
    with patch("requests.Session.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response
        mock_get.return_value = mock_response

        service = APIService()
        recipe = service.get_random_recipe()

        if api_response["meals"]:
            assert isinstance(recipe, Recipe)
            assert recipe.id == api_response["meals"][0]["idMeal"]
        else:
            assert recipe is None

# New test cases for exception handling and edge cases

@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(error=error_strategy)
def test_get_random_recipe_exception_handling(error):
    """Test error handling in get_random_recipe method"""
    with patch("requests.Session.get") as mock_get:
        mock_get.side_effect = error
        
        service = APIService()
        recipe = service.get_random_recipe()
        
        assert recipe is None

@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    search_term=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_ "), min_size=1, max_size=50),
    error=error_strategy
)
def test_search_recipes_by_name_exception_handling(search_term, error):
    """Test error handling in search_recipes_by_name method"""
    with patch("requests.Session.get") as mock_get:
        mock_get.side_effect = error
        
        service = APIService()
        recipes = service.search_recipes_by_name(search_term)
        
        assert isinstance(recipes, list)
        assert len(recipes) == 0

@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    ingredient=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_ "), min_size=1, max_size=50),
    error=error_strategy
)
def test_search_recipes_by_ingredient_exception_handling(ingredient, error):
    """Test error handling in search_recipes_by_ingredient method"""
    with patch("requests.Session.get") as mock_get:
        mock_get.side_effect = error
        
        service = APIService()
        recipes = service.search_recipes_by_ingredient(ingredient)
        
        assert isinstance(recipes, list)
        assert len(recipes) == 0

@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    search_term=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_ "), min_size=1, max_size=50),
    status_code=st.integers(min_value=400, max_value=599)
)
def test_search_recipes_by_name_http_error(search_term, status_code):
    """Test handling of HTTP errors in search_recipes_by_name method"""
    with patch("requests.Session.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_get.return_value = mock_response
        
        service = APIService()
        recipes = service.search_recipes_by_name(search_term)
        
        assert isinstance(recipes, list)
        assert len(recipes) == 0

@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    ingredient=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_ "), min_size=1, max_size=50),
    status_code=st.integers(min_value=400, max_value=599)
)
def test_search_recipes_by_ingredient_http_error(ingredient, status_code):
    """Test handling of HTTP errors in search_recipes_by_ingredient method"""
    with patch("requests.Session.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_get.return_value = mock_response
        
        service = APIService()
        recipes = service.search_recipes_by_ingredient(ingredient)
        
        assert isinstance(recipes, list)
        assert len(recipes) == 0

@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(status_code=st.integers(min_value=400, max_value=599))
def test_get_random_recipe_http_error(status_code):
    """Test handling of HTTP errors in get_random_recipe method"""
    with patch("requests.Session.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_get.return_value = mock_response
        
        service = APIService()
        recipe = service.get_random_recipe()
        
        assert recipe is None

@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    meal=st.fixed_dictionaries({
        "idMeal": st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"), min_size=1, max_size=10),
        "strMeal": st.text(min_size=1, max_size=100),
        "strMealThumb": st.text(min_size=1, max_size=200),
        "strInstructions": st.text(min_size=1, max_size=1000),
        **{f"strIngredient{i}": st.text(min_size=0, max_size=0) for i in range(1, 21)},
        **{f"strMeasure{i}": st.text(min_size=0, max_size=0) for i in range(1, 21)},
    })
)
def test_parse_meal_to_recipe_empty_ingredients(meal):
    """Test parsing of meal data with empty ingredients"""
    service = APIService()
    recipe = service._parse_meal_to_recipe(meal)
    
    assert isinstance(recipe, Recipe)
    assert recipe.id == meal["idMeal"]
    assert isinstance(recipe.ingredients, list)
    assert len(recipe.ingredients) == 0

@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    meal=st.fixed_dictionaries({
        "idMeal": st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"), min_size=1, max_size=10),
        "strMeal": st.text(min_size=1, max_size=100),
        "strMealThumb": st.text(min_size=1, max_size=200),
        "strInstructions": st.text(min_size=1, max_size=1000),
        **{f"strIngredient{i}": st.text(min_size=1, max_size=50) if i <= 10 else st.none() for i in range(1, 21)},
        **{f"strMeasure{i}": st.none() for i in range(1, 21)},
    })
)
def test_parse_meal_to_recipe_no_measures(meal):
    """Test parsing of meal data with ingredients but no measurements"""
    service = APIService()
    recipe = service._parse_meal_to_recipe(meal)
    
    assert isinstance(recipe, Recipe)
    assert isinstance(recipe.ingredients, list)
    assert len(recipe.ingredients) > 0
    # Ingredients should just be the ingredient name without measures
    for i in range(1, 11):
        ing_value = meal.get(f"strIngredient{i}")
        if ing_value and ing_value.strip():
            assert ing_value.strip() in recipe.ingredients
