from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.models.recipe import Recipe

# Define strategies for each field
id_strategy = st.text(min_size=1, max_size=50)
name_strategy = st.text(min_size=1, max_size=100)
url_strategy = st.text(min_size=1, max_size=200)  # Removed http filter
instructions_strategy = st.text(min_size=1, max_size=1000)
ingredients_strategy = st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=20)


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    id=id_strategy,
    name=name_strategy,
    image_url=url_strategy,
    instructions=instructions_strategy,
    ingredients=ingredients_strategy,
    is_favorite=st.booleans(),
    is_custom=st.booleans(),
)
def test_recipe_creation_fuzzing(id, name, image_url, instructions, ingredients, is_favorite, is_custom):
    """Test Recipe creation with fuzzed inputs"""
    recipe = Recipe(
        id=id,
        name=name,
        image_url=image_url,
        instructions=instructions,
        ingredients=ingredients,
        is_favorite=is_favorite,
        is_custom=is_custom,
    )

    # Verify all fields are set correctly
    assert recipe.id == id
    assert recipe.name == name
    assert recipe.image_url == image_url
    assert recipe.instructions == instructions
    assert recipe.ingredients == ingredients
    assert recipe.is_favorite == is_favorite
    assert recipe.is_custom == is_custom


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    recipe_dict=st.fixed_dictionaries(
        {
            "id": id_strategy,
            "name": name_strategy,
            "image_url": url_strategy,
            "instructions": instructions_strategy,
            "ingredients": ingredients_strategy,
            "is_favorite": st.booleans(),
            "is_custom": st.booleans(),
        }
    )
)
def test_recipe_from_dict_fuzzing(recipe_dict):
    """Test Recipe.from_dict with fuzzed inputs"""
    recipe = Recipe.from_dict(recipe_dict)

    # Verify all fields are set correctly
    assert recipe.id == recipe_dict["id"]
    assert recipe.name == recipe_dict["name"]
    assert recipe.image_url == recipe_dict["image_url"]
    assert recipe.instructions == recipe_dict["instructions"]
    assert recipe.ingredients == recipe_dict["ingredients"]
    assert recipe.is_favorite == recipe_dict["is_favorite"]
    assert recipe.is_custom == recipe_dict["is_custom"]


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    id=id_strategy,
    name=name_strategy,
    image_url=url_strategy,
    instructions=instructions_strategy,
    ingredients=ingredients_strategy,
    is_favorite=st.booleans(),
    is_custom=st.booleans(),
)
def test_recipe_to_dict_fuzzing(id, name, image_url, instructions, ingredients, is_favorite, is_custom):
    """Test Recipe.to_dict with fuzzed inputs"""
    recipe = Recipe(
        id=id,
        name=name,
        image_url=image_url,
        instructions=instructions,
        ingredients=ingredients,
        is_favorite=is_favorite,
        is_custom=is_custom,
    )

    recipe_dict = recipe.to_dict()

    # Verify all fields are in the dictionary
    assert recipe_dict["id"] == id
    assert recipe_dict["name"] == name
    assert recipe_dict["image_url"] == image_url
    assert recipe_dict["instructions"] == instructions
    assert recipe_dict["ingredients"] == ingredients
    assert recipe_dict["is_favorite"] == is_favorite
    assert recipe_dict["is_custom"] == is_custom
