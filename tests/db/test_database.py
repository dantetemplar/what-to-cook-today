import os
import tempfile

import pytest

from src.db.database import Database
from src.models.recipe import Recipe


@pytest.fixture
def temp_db():
    # Create a temporary file for the database
    fd, path = tempfile.mkstemp()
    try:
        db = Database(db_path=path)
        yield db
    finally:
        # Clean up
        os.close(fd)
        os.unlink(path)


@pytest.fixture
def sample_recipe():
    return Recipe(
        id="123",
        name="Test Recipe",
        image_url="http://example.com/image.jpg",
        instructions="Test instructions",
        ingredients=["ingredient1", "ingredient2"],
    )


def test_add_recipe(temp_db, sample_recipe):
    temp_db.add_recipe(sample_recipe)
    retrieved_recipe = temp_db.get_recipe("123")
    assert retrieved_recipe is not None
    assert retrieved_recipe.id == sample_recipe.id
    assert retrieved_recipe.name == sample_recipe.name
    assert retrieved_recipe.image_url == sample_recipe.image_url
    assert retrieved_recipe.instructions == sample_recipe.instructions
    assert retrieved_recipe.ingredients == sample_recipe.ingredients


def test_get_nonexistent_recipe(temp_db):
    assert temp_db.get_recipe("nonexistent") is None


def test_get_all_recipes(temp_db, sample_recipe):
    # Add multiple recipes
    recipe2 = Recipe(
        id="456",
        name="Another Recipe",
        image_url="http://example.com/image2.jpg",
        instructions="More instructions",
        ingredients=["ingredient3", "ingredient4"],
    )

    temp_db.add_recipe(sample_recipe)
    temp_db.add_recipe(recipe2)

    all_recipes = temp_db.get_all_recipes()
    assert len(all_recipes) == 2
    assert any(r.id == "123" for r in all_recipes)
    assert any(r.id == "456" for r in all_recipes)


def test_toggle_favorite(temp_db, sample_recipe):
    temp_db.add_recipe(sample_recipe)

    # Toggle favorite
    assert temp_db.toggle_favorite("123", "test_user")
    favorites = temp_db.get_favorite_recipes("test_user")
    assert len(favorites) == 1
    assert favorites[0].id == "123"

    # Toggle back
    assert temp_db.toggle_favorite("123", "test_user")
    favorites = temp_db.get_favorite_recipes("test_user")
    assert len(favorites) == 0


def test_get_favorite_recipes(temp_db, sample_recipe):
    # Add a favorite recipe and a non-favorite recipe
    favorite_recipe = Recipe(
        id="456",
        name="Favorite Recipe",
        image_url="http://example.com/image2.jpg",
        instructions="More instructions",
        ingredients=["ingredient3", "ingredient4"],
    )

    temp_db.add_recipe(sample_recipe)
    temp_db.add_recipe(favorite_recipe)
    
    # Add favorite for test_user
    temp_db.toggle_favorite("456", "test_user")

    favorites = temp_db.get_favorite_recipes("test_user")
    assert len(favorites) == 1
    assert favorites[0].id == "456"


def test_get_custom_recipes(temp_db, sample_recipe):
    # Add a custom recipe and a non-custom recipe
    custom_recipe = Recipe(
        id="456",
        name="Custom Recipe",
        image_url="http://example.com/image2.jpg",
        instructions="More instructions",
        ingredients=["ingredient3", "ingredient4"],
        is_custom=True,
    )

    temp_db.add_recipe(sample_recipe)
    temp_db.add_recipe(custom_recipe)

    customs = temp_db.get_custom_recipes()
    assert len(customs) == 1
    assert customs[0].id == "456"


def test_get_favorite_recipes_with_user_id(temp_db, sample_recipe):
    # Add a recipe
    temp_db.add_recipe(sample_recipe)
    
    # Add favorite for user1
    assert temp_db.toggle_favorite(sample_recipe.id, "user1")
    
    # Add favorite for user2
    assert temp_db.toggle_favorite(sample_recipe.id, "user2")
    
    # Get favorites for user1
    favorites_user1 = temp_db.get_favorite_recipes("user1")
    assert len(favorites_user1) == 1
    assert favorites_user1[0].id == sample_recipe.id
    
    # Get favorites for user2
    favorites_user2 = temp_db.get_favorite_recipes("user2")
    assert len(favorites_user2) == 1
    assert favorites_user2[0].id == sample_recipe.id


def test_toggle_favorite_with_user_id(temp_db, sample_recipe):
    # Add a recipe
    temp_db.add_recipe(sample_recipe)
    
    # Toggle favorite for user1
    assert temp_db.toggle_favorite(sample_recipe.id, "user1")
    
    # Verify it's favorited for user1
    favorites_user1 = temp_db.get_favorite_recipes("user1")
    assert len(favorites_user1) == 1
    
    # Verify it's not favorited for user2
    favorites_user2 = temp_db.get_favorite_recipes("user2")
    assert len(favorites_user2) == 0
    
    # Toggle back for user1
    assert temp_db.toggle_favorite(sample_recipe.id, "user1")
    
    # Verify it's no longer favorited for user1
    favorites_user1 = temp_db.get_favorite_recipes("user1")
    assert len(favorites_user1) == 0


def test_toggle_favorite_nonexistent_recipe(temp_db):
    # Try to toggle favorite for a nonexistent recipe
    assert not temp_db.toggle_favorite("nonexistent", "user1")
