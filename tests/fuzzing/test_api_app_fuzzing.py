from unittest.mock import patch

from fastapi.testclient import TestClient
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.api.app import app
from src.models.recipe import Recipe

client = TestClient(app)

# Define strategies for recipe data - use URL-safe characters only
recipe_id_strategy = st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"), min_size=1, max_size=10)
recipe_name_strategy = st.text(min_size=1, max_size=100)
recipe_image_url_strategy = st.one_of(st.text(min_size=1, max_size=200), st.none())
recipe_instructions_strategy = st.text(min_size=1, max_size=1000)
recipe_ingredients_strategy = st.lists(st.text(min_size=1, max_size=100), min_size=0, max_size=20)
user_id_strategy = st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"), min_size=1, max_size=20)

# Strategy for search parameters
search_param_strategy = st.one_of(
    st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_ "), min_size=1, max_size=50),
    st.none()
)

# Recipe objects strategy
recipe_object_strategy = st.builds(
    Recipe,
    id=recipe_id_strategy,
    name=recipe_name_strategy,
    image_url=recipe_image_url_strategy,
    instructions=recipe_instructions_strategy,
    ingredients=recipe_ingredients_strategy,
    is_favorite=st.booleans(),
    is_custom=st.booleans()
)

# Recipe response strategy for API
recipe_response_strategy = st.builds(
    lambda id, name, image_url, instructions, ingredients, is_favorite, is_custom: {
        "id": id,
        "name": name,
        "image_url": image_url,
        "instructions": instructions,
        "ingredients": ingredients,
        "is_favorite": is_favorite,
        "is_custom": is_custom
    },
    id=recipe_id_strategy,
    name=recipe_name_strategy,
    image_url=recipe_image_url_strategy,
    instructions=recipe_instructions_strategy,
    ingredients=recipe_ingredients_strategy,
    is_favorite=st.booleans(),
    is_custom=st.booleans()
)

@settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
@given(recipe=recipe_object_strategy)
def test_get_random_recipe_endpoint_fuzzing(recipe):
    """Test the random recipe endpoint with fuzzed input"""
    with patch("src.services.api_service.APIService.get_random_recipe") as mock_get_random:
        with patch("src.db.database.Database.add_recipe") as mock_add_recipe:
            mock_get_random.return_value = recipe
            mock_add_recipe.return_value = True
            
            response = client.get("/recipes/random")
            
            if recipe:
                assert response.status_code == 200
                result = response.json()
                assert result["id"] == recipe.id
                assert result["name"] == recipe.name
                assert result["instructions"] == recipe.instructions
                mock_add_recipe.assert_called_once()
            else:
                assert response.status_code == 404

@settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
@given(
    name=search_param_strategy,
    ingredient=search_param_strategy,
    include_ingredients=search_param_strategy,
    exclude_ingredients=search_param_strategy,
    recipes_by_name=st.lists(recipe_object_strategy, min_size=0, max_size=5),
    recipes_by_ingredient=st.lists(recipe_object_strategy, min_size=0, max_size=5),
    all_recipes=st.lists(recipe_object_strategy, min_size=0, max_size=5)
)
def test_search_recipes_endpoint_fuzzing(name, ingredient, include_ingredients, exclude_ingredients, 
                                        recipes_by_name, recipes_by_ingredient, all_recipes):
    """Test the search recipes endpoint with fuzzed inputs"""
    with patch("src.services.api_service.APIService.search_recipes_by_name") as mock_search_by_name:
        with patch("src.services.api_service.APIService.search_recipes_by_ingredient") as mock_search_by_ingredient:
            with patch("src.db.database.Database.get_all_recipes") as mock_get_all:
                with patch("src.db.database.Database.add_recipe") as mock_add_recipe:
                    mock_search_by_name.return_value = recipes_by_name
                    mock_search_by_ingredient.return_value = recipes_by_ingredient
                    mock_get_all.return_value = all_recipes
                    mock_add_recipe.return_value = True
                    
                    # Build query parameters
                    params = {}
                    if name is not None:
                        params["name"] = name
                    if ingredient is not None:
                        params["ingredient"] = ingredient
                    if include_ingredients is not None:
                        params["include_ingredients"] = include_ingredients
                    if exclude_ingredients is not None:
                        params["exclude_ingredients"] = exclude_ingredients
                    
                    response = client.get("/recipes/search", params=params)
                    assert response.status_code == 200
                    results = response.json()
                    assert isinstance(results, list)
                    
                    # Verify correct API calls based on parameters
                    if name is not None:
                        mock_search_by_name.assert_called_with(name)
                    else:
                        mock_search_by_name.assert_not_called()
                        
                    if ingredient is not None:
                        mock_search_by_ingredient.assert_called_with(ingredient)
                    elif include_ingredients is not None and ingredient is None:
                        assert mock_search_by_ingredient.call_count > 0

@settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
@given(
    user_id=user_id_strategy,
    recipes=st.lists(recipe_object_strategy, min_size=0, max_size=5)
)
def test_get_favorite_recipes_endpoint_fuzzing(user_id, recipes):
    """Test the favorite recipes endpoint with fuzzed inputs"""
    with patch("src.db.database.Database.get_favorite_recipes") as mock_get_favorites:
        mock_get_favorites.return_value = recipes
        
        response = client.get(f"/recipes/favorites?user_id={user_id}")
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        assert len(results) == len(recipes)
        
        mock_get_favorites.assert_called_once_with(user_id)

@settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
@given(
    recipes=st.lists(recipe_object_strategy, min_size=0, max_size=5)
)
def test_get_custom_recipes_endpoint_fuzzing(recipes):
    """Test the custom recipes endpoint with fuzzed inputs"""
    with patch("src.db.database.Database.get_custom_recipes") as mock_get_custom:
        mock_get_custom.return_value = recipes
        
        response = client.get("/recipes/custom")
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        assert len(results) == len(recipes)
        
        mock_get_custom.assert_called_once()

@settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
@given(
    recipe_id=recipe_id_strategy,
    user_id=user_id_strategy,
    success=st.booleans()
)
def test_toggle_favorite_endpoint_fuzzing(recipe_id, user_id, success):
    """Test the toggle favorite endpoint with fuzzed inputs"""
    with patch("src.db.database.Database.toggle_favorite") as mock_toggle:
        mock_toggle.return_value = success
        
        response = client.post(
            f"/recipes/{recipe_id}/favorite", 
            json={"user_id": user_id}
        )
        
        if success:
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
        else:
            assert response.status_code == 404
        
        mock_toggle.assert_called_once_with(recipe_id, user_id)

@settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
@given(recipe=recipe_response_strategy)
def test_add_custom_recipe_endpoint_fuzzing(recipe):
    """Test adding a custom recipe with fuzzed inputs"""
    with patch("src.db.database.Database.add_recipe") as mock_add:
        mock_add.return_value = True
        
        response = client.post("/recipes/custom", json=recipe)
        assert response.status_code == 200
        result = response.json()
        
        assert result["id"] == recipe["id"]
        assert result["name"] == recipe["name"]
        assert result["instructions"] == recipe["instructions"]
        
        mock_add.assert_called_once()

@settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
@given(
    user_id=user_id_strategy,
    favorite_recipes=st.lists(recipe_object_strategy, min_size=0, max_size=5)
)
def test_random_favorite_recipe_endpoint_fuzzing(user_id, favorite_recipes):
    """Test the random favorite recipe endpoint with fuzzed inputs"""
    with patch("src.db.database.Database.get_favorite_recipes") as mock_get_favorites:
        mock_get_favorites.return_value = favorite_recipes
        
        response = client.get(f"/recipes/random_from_favorites?user_id={user_id}")
        
        if favorite_recipes:
            assert response.status_code == 200
            # Since random.choice is used in the endpoint, we can't assert the exact recipe
            # But we can check the response is valid
            result = response.json()
            if not isinstance(result, dict) or "error" not in result:
                assert any(r.id == result.get("id", None) for r in favorite_recipes)
        else:
            assert response.status_code == 200
            result = response.json()
            assert "error" in result
            assert result["error"] == "No favorite recipes found."
        
        mock_get_favorites.assert_called_once_with(user_id)

@settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
@given(
    user_id=user_id_strategy,
    custom_recipes=st.lists(recipe_object_strategy, min_size=0, max_size=5)
)
def test_random_custom_recipe_endpoint_fuzzing(user_id, custom_recipes):
    """Test the random custom recipe endpoint with fuzzed inputs"""
    with patch("src.db.database.Database.get_custom_recipes") as mock_get_custom:
        mock_get_custom.return_value = custom_recipes
        
        response = client.get(f"/recipes/random_from_custom?user_id={user_id}")
        
        if custom_recipes:
            assert response.status_code == 200
            # Since random.choice is used in the endpoint, we can't assert the exact recipe
            # But we can check the response is valid
            result = response.json()
            if not isinstance(result, dict) or "error" not in result:
                assert any(r.id == result.get("id", None) for r in custom_recipes)
        else:
            assert response.status_code == 200
            result = response.json()
            assert "error" in result
            assert result["error"] == "No custom recipes found."
        
        # Make sure we pass the user_id to the get_custom_recipes call
        mock_get_custom.assert_called_once_with(user_id) 