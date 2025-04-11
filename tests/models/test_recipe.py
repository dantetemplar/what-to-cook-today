from src.models.recipe import Recipe


def test_recipe_creation():
    recipe = Recipe(
        id="123",
        name="Test Recipe",
        image_url="http://example.com/image.jpg",
        instructions="Test instructions",
        ingredients=["ingredient1", "ingredient2"],
    )
    assert recipe.id == "123"
    assert recipe.name == "Test Recipe"
    assert recipe.image_url == "http://example.com/image.jpg"
    assert recipe.instructions == "Test instructions"
    assert recipe.ingredients == ["ingredient1", "ingredient2"]
    assert not recipe.is_favorite
    assert not recipe.is_custom


def test_recipe_to_dict():
    recipe = Recipe(
        id="123",
        name="Test Recipe",
        image_url="http://example.com/image.jpg",
        instructions="Test instructions",
        ingredients=["ingredient1", "ingredient2"],
        is_favorite=True,
        is_custom=True,
    )
    recipe_dict = recipe.to_dict()
    assert recipe_dict == {
        "id": "123",
        "name": "Test Recipe",
        "image_url": "http://example.com/image.jpg",
        "instructions": "Test instructions",
        "ingredients": ["ingredient1", "ingredient2"],
        "is_favorite": True,
        "is_custom": True,
    }


def test_recipe_from_dict():
    recipe_dict = {
        "id": "123",
        "name": "Test Recipe",
        "image_url": "http://example.com/image.jpg",
        "instructions": "Test instructions",
        "ingredients": ["ingredient1", "ingredient2"],
        "is_favorite": True,
        "is_custom": True,
    }
    recipe = Recipe.from_dict(recipe_dict)
    assert recipe.id == "123"
    assert recipe.name == "Test Recipe"
    assert recipe.image_url == "http://example.com/image.jpg"
    assert recipe.instructions == "Test instructions"
    assert recipe.ingredients == ["ingredient1", "ingredient2"]
    assert recipe.is_favorite
    assert recipe.is_custom
