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


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    recipe_dict=st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(
            st.text(),
            st.integers(),
            st.floats(),
            st.booleans(),
            st.lists(st.text()),
            st.none(),
        ),
        min_size=1,
        max_size=10,
    )
)
def test_recipe_from_dict_invalid_inputs(recipe_dict):
    """Test Recipe.from_dict with invalid dictionary inputs"""
    try:
        Recipe.from_dict(recipe_dict)
        # If we get here, the input was valid
        assert all(key in recipe_dict for key in ["id", "name", "instructions", "ingredients"])
    except (KeyError, TypeError, ValueError):
        # Expected for invalid inputs
        pass


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    text=st.text(min_size=0, max_size=1000).filter(lambda x: any(c in x for c in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"))
)
def test_recipe_with_special_characters(text):
    """Test Recipe creation with special characters in text fields"""
    recipe = Recipe(
        id=text[:50],
        name=text[:100],
        image_url=text[:200],
        instructions=text[:1000],
        ingredients=[text[:50]],
        is_favorite=False,
        is_custom=False,
    )
    
    assert recipe.id == text[:50]
    assert recipe.name == text[:100]
    assert recipe.image_url == text[:200]
    assert recipe.instructions == text[:1000]
    assert recipe.ingredients == [text[:50]]


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    ingredients=st.lists(
        st.text(min_size=0, max_size=50),
        min_size=0,
        max_size=100,
    )
)
def test_recipe_empty_ingredients(ingredients):
    """Test Recipe creation with empty or varying length ingredients list"""
    try:
        recipe = Recipe(
            id="test",
            name="test",
            image_url="test",
            instructions="test",
            ingredients=ingredients,
            is_favorite=False,
            is_custom=False,
        )
        assert recipe.ingredients == ingredients
    except ValueError:
        # Expected if ingredients list is empty
        assert len(ingredients) == 0


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    text=st.text(min_size=0, max_size=1)
)
def test_recipe_minimal_text_fields(text):
    """Test Recipe creation with minimal length text fields"""
    recipe = Recipe(
        id=text,
        name=text,
        image_url=text,
        instructions=text,
        ingredients=[text],
        is_favorite=False,
        is_custom=False,
    )
    
    assert recipe.id == text
    assert recipe.name == text
    assert recipe.image_url == text
    assert recipe.instructions == text
    assert recipe.ingredients == [text]


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    recipe_dict=st.fixed_dictionaries(
        {
            "id": id_strategy,
            "name": name_strategy,
            "image_url": st.one_of(st.none(), url_strategy),
            "instructions": instructions_strategy,
            "ingredients": ingredients_strategy,
            "is_favorite": st.booleans(),
            "is_custom": st.booleans(),
        }
    )
)
def test_recipe_nullable_fields(recipe_dict):
    """Test Recipe creation with nullable fields"""
    recipe = Recipe.from_dict(recipe_dict)
    assert recipe.image_url == recipe_dict["image_url"]
