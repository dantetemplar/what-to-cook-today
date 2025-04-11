from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import app
from src.models.recipe import Recipe


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_recipe():
    return Recipe(
        id="123",
        name="Test Recipe",
        image_url="http://example.com/image.jpg",
        instructions="Test instructions",
        ingredients=["ingredient1", "ingredient2"],
    )


def test_get_random_recipe(client, sample_recipe):
    with patch("src.api.app.api_service.get_random_recipe") as mock_get_random:
        mock_get_random.return_value = sample_recipe

        response = client.get("/recipes/random")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "123"
        assert data["name"] == "Test Recipe"
        assert data["image_url"] == "http://example.com/image.jpg"
        assert data["instructions"] == "Test instructions"
        assert data["ingredients"] == ["ingredient1", "ingredient2"]


def test_get_random_recipe_not_found(client):
    with patch("src.api.app.api_service.get_random_recipe") as mock_get_random:
        mock_get_random.return_value = None

        response = client.get("/recipes/random")
        assert response.status_code == 404


def test_search_recipes_by_name(client, sample_recipe):
    with patch("src.api.app.api_service.search_recipes_by_name") as mock_search:
        mock_search.return_value = [sample_recipe]

        response = client.get("/recipes/search?name=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Recipe"


def test_search_recipes_by_ingredient(client, sample_recipe):
    with patch("src.api.app.api_service.search_recipes_by_ingredient") as mock_search:
        mock_search.return_value = [sample_recipe]

        response = client.get("/recipes/search?ingredient=ingredient1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Recipe"


def test_get_favorite_recipes(client, sample_recipe):
    with patch("src.api.app.db.get_favorite_recipes") as mock_get_favorites:
        mock_get_favorites.return_value = [sample_recipe]

        response = client.get("/recipes/favorites?user_id=test_user")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Recipe"
        mock_get_favorites.assert_called_once_with("test_user")


def test_get_custom_recipes(client, sample_recipe):
    with patch("src.api.app.db.get_custom_recipes") as mock_get_custom:
        mock_get_custom.return_value = [sample_recipe]

        response = client.get("/recipes/custom")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Recipe"


def test_toggle_favorite_success(client):
    with patch("src.api.app.db.toggle_favorite") as mock_toggle:
        mock_toggle.return_value = True

        response = client.post("/recipes/123/favorite", json={"user_id": "test_user"})
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        mock_toggle.assert_called_once_with("123", "test_user")


def test_toggle_favorite_not_found(client):
    with patch("src.api.app.db.toggle_favorite") as mock_toggle:
        mock_toggle.return_value = False

        response = client.post("/recipes/123/favorite", json={"user_id": "test_user"})
        assert response.status_code == 404
        mock_toggle.assert_called_once_with("123", "test_user")


def test_toggle_favorite_missing_user_id(client):
    response = client.post("/recipes/123/favorite")
    assert response.status_code == 422  # Validation error for missing user_id


def test_add_custom_recipe(client):
    custom_recipe = {
        "id": "123",
        "name": "Custom Recipe",
        "image_url": "http://example.com/image.jpg",
        "instructions": "Test instructions",
        "ingredients": ["ingredient1", "ingredient2"],
        "is_favorite": False,
        "is_custom": True,
    }

    with patch("src.api.app.db.add_recipe") as mock_add:
        response = client.post("/recipes/custom", json=custom_recipe)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Custom Recipe"
        assert data["is_custom"]
