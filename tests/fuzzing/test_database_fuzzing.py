import os
import tempfile
import uuid

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.db.database import Database
from src.models.recipe import Recipe

# Define strategies for database testing
recipe_strategy = st.builds(
    Recipe,
    id=st.text(min_size=1, max_size=50).map(lambda s: f"{s}_{uuid.uuid4()}"),
    name=st.text(min_size=1, max_size=100),
    image_url=st.one_of(st.text(min_size=1, max_size=200), st.none()),
    instructions=st.text(min_size=1, max_size=1000),
    ingredients=st.lists(
        st.text(min_size=1, max_size=50).filter(lambda x: "," not in x), 
        min_size=1, 
        max_size=20
    ),
    is_favorite=st.booleans(),
    is_custom=st.booleans(),
)

user_id_strategy = st.text(min_size=1, max_size=50)


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(recipe=recipe_strategy)
def test_add_and_get_recipe_fuzzing(recipe):
    """Test adding and retrieving a recipe with fuzzed inputs"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db = Database(tmp.name)
        try:
            db.add_recipe(recipe)
            retrieved_recipe = db.get_recipe(recipe.id)
            
            assert retrieved_recipe is not None
            assert retrieved_recipe.id == recipe.id
            assert retrieved_recipe.name == recipe.name
            assert retrieved_recipe.image_url == recipe.image_url
            assert retrieved_recipe.instructions == recipe.instructions
            # Compare ingredients as sets to handle order differences
            assert set(retrieved_recipe.ingredients) == set(recipe.ingredients)
            assert retrieved_recipe.is_custom == recipe.is_custom
        finally:
            os.unlink(tmp.name)


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    recipes=st.lists(recipe_strategy, min_size=1, max_size=10, unique_by=lambda r: r.id),
    user_id=user_id_strategy
)
def test_favorite_recipes_fuzzing(recipes, user_id):
    """Test favorite recipes functionality with fuzzed inputs"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db = Database(tmp.name)
        try:
            # Add recipes
            for recipe in recipes:
                db.add_recipe(recipe)
            
            # Toggle favorites for each recipe
            for recipe in recipes:
                db.toggle_favorite(recipe.id, user_id)
            
            # Get favorite recipes
            favorite_recipes = db.get_favorite_recipes(user_id)
            
            # Verify favorites
            assert len(favorite_recipes) == len(recipes)
            favorite_ids = {recipe.id for recipe in favorite_recipes}
            recipe_ids = {recipe.id for recipe in recipes}
            assert favorite_ids == recipe_ids
            
            # Toggle favorites off
            for recipe in recipes:
                db.toggle_favorite(recipe.id, user_id)
            
            # Verify no favorites remain
            assert len(db.get_favorite_recipes(user_id)) == 0
        finally:
            os.unlink(tmp.name)


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    recipes=st.lists(recipe_strategy, min_size=1, max_size=10, unique_by=lambda r: r.id),
    user_id=user_id_strategy
)
def test_custom_recipes_fuzzing(recipes, user_id):
    """Test custom recipes functionality with fuzzed inputs"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db = Database(tmp.name)
        try:
            # Add recipes
            for recipe in recipes:
                db.add_recipe(recipe)
            
            # Get custom recipes
            custom_recipes = db.get_custom_recipes(user_id)
            
            # Verify only custom recipes are returned
            custom_recipe_ids = {recipe.id for recipe in custom_recipes}
            expected_custom_ids = {recipe.id for recipe in recipes if recipe.is_custom}
            assert custom_recipe_ids == expected_custom_ids
        finally:
            os.unlink(tmp.name)


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    recipe=recipe_strategy,
    user_id=user_id_strategy
)
def test_invalid_recipe_operations_fuzzing(recipe, user_id):
    """Test operations with invalid recipe IDs"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db = Database(tmp.name)
        try:
            # Test getting non-existent recipe
            assert db.get_recipe(recipe.id) is None
            
            # Test toggling favorite for non-existent recipe
            assert not db.toggle_favorite(recipe.id, user_id)
            
            # Test getting favorites for non-existent recipe
            assert len(db.get_favorite_recipes(user_id)) == 0
        finally:
            os.unlink(tmp.name)


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    recipes=st.lists(recipe_strategy, min_size=1, max_size=10, unique_by=lambda r: r.id)
)
def test_get_all_recipes_fuzzing(recipes):
    """Test getting all recipes with fuzzed inputs"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db = Database(tmp.name)
        try:
            # Add recipes
            for recipe in recipes:
                db.add_recipe(recipe)
            
            # Get all recipes
            all_recipes = db.get_all_recipes()
            
            # Verify all recipes are returned
            assert len(all_recipes) == len(recipes)
            all_recipe_ids = {recipe.id for recipe in all_recipes}
            recipe_ids = {recipe.id for recipe in recipes}
            assert all_recipe_ids == recipe_ids
            
            # Verify recipe contents
            for recipe in all_recipes:
                original_recipe = next(r for r in recipes if r.id == recipe.id)
                assert recipe.name == original_recipe.name
                assert recipe.instructions == original_recipe.instructions
                assert set(recipe.ingredients) == set(original_recipe.ingredients)
        finally:
            os.unlink(tmp.name) 