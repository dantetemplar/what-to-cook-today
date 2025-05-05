from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.ui.app import (
    display_recipe,
    generate_pdf,
    get_favorite_recipes,
    get_random_recipe_from_custom,
    get_random_recipe_from_favorites,
    refresh_favorites,
)


@pytest.fixture
def mock_client():
    with patch("src.ui.app.get_client") as mock:
        yield mock

@pytest.fixture
def mock_session_state():
    with patch("src.ui.app.st.session_state", new={}) as mock:
        yield mock

def test_generate_pdf():
    recipes = [
        {
            "name": "Trenbalon ZaVtrak",
            "ingredients": ["5 eggs", "250 grams whey protein", "1ml testosteron"],
            "instructions": ["Mix ingredients", "intravenous injection"],
            "image_url": "http://example.com/image.jpg",
        }
    ]
    title = "Trenbalon ZaVtrak"

    pdf_data = generate_pdf(recipes, title)
    assert pdf_data is not None
    assert isinstance(pdf_data, bytes)

def test_display_recipe():
    with patch("src.ui.app.st") as mock_st:
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        recipe = {
            "name": "Trenbalon ZaVtrak",
            "ingredients": ["5 eggs", "250 grams whey protein", "1ml testosteron"],
            "instructions": ["Mix ingredients", "Intravenous injection"],
            "image_url": "http://example.com/image.jpg",
        }
        display_recipe(recipe)

        mock_st.subheader.assert_called_once_with("Trenbalon ZaVtrak")
        mock_st.image.assert_called_once_with("http://example.com/image.jpg", use_container_width=True)
        mock_st.write.assert_any_call("### Ingredients")
        mock_st.write.assert_any_call("- 5 eggs")
        mock_st.write.assert_any_call("- 250 grams whey protein")
        mock_st.write.assert_any_call("- 1ml testosteron")
        mock_st.write.assert_any_call("### Instructions")
        mock_st.markdown.assert_any_call("1. Mix ingredients")
        mock_st.markdown.assert_any_call("2. Intravenous injection")

def test_get_random_recipe_from_favorites(mock_client):
    with patch("src.ui.app.get_user_id", return_value=None):
        mock_client.return_value.get.return_value.json.return_value = {"id": "777", "name": "My super random favorite recipe"}
        mock_client.return_value.get.return_value.raise_for_status = MagicMock()

        recipe = get_random_recipe_from_favorites()

        assert recipe["id"] == "777"
        assert recipe["name"] == "My super random favorite recipe"
        mock_client.return_value.get.assert_called_once_with("/recipes/random_from_favorites?user_id=None")

def test_get_random_recipe_from_custom(mock_client):
    with patch("src.ui.app.get_user_id", return_value=None):
        mock_client.return_value.get.return_value.json.return_value = {"id": "777", "name": "My super random favorite recipe"}
        mock_client.return_value.get.return_value.raise_for_status = MagicMock()

        recipe = get_random_recipe_from_custom()

        assert recipe["id"] == "777"
        assert recipe["name"] == "My super random favorite recipe"
        mock_client.return_value.get.assert_called_once_with("/recipes/random_from_custom?user_id=None")

def test_refresh_favorites(mock_client, mock_session_state):
    mock_client.return_value.get.return_value.json.return_value = [{"id": "777", "name": "My super random favorite recipe"}]
    mock_client.return_value.get.return_value.raise_for_status = MagicMock()

    refresh_favorites()

    assert "favorites" in mock_session_state
    assert mock_session_state["favorites"] == {"777": {"id": "777", "name": "My super random favorite recipe"}}

def test_get_favorite_recipes(mock_session_state):
    mock_session_state["favorites"] = {"777": {"id": "777", "name": "My super random favorite recipe"}}

    favorites = get_favorite_recipes()

    assert len(favorites) == 1
    assert favorites[0]["id"] == "777"
    assert favorites[0]["name"] == "My super random favorite recipe"

def test_is_favorite(mock_session_state):
    mock_session_state["favorites"] = {"777": {"id": "777", "name": "My super random favorite recipe"}}

    from src.ui.app import is_favorite

    assert is_favorite("777") is True
    assert is_favorite("999") is False

def test_add_custom_recipe(mock_client):
    from src.ui.app import add_custom_recipe

    mock_client.return_value.post.return_value.raise_for_status = MagicMock()

    recipe = {
        "name": "Custom Recipe",
        "ingredients": ["5 eggs"],
        "instructions": ["Mix ingredients", "fry for 10 minutes over high heat, stirring"],
    }

    result = add_custom_recipe(recipe)

    assert result is True
    mock_client.return_value.post.assert_called_once_with("/recipes/custom", json=recipe)

def test_handle_favorite_click(mock_session_state, mock_client):
    from src.ui.app import handle_favorite_click

    mock_client.return_value.post.return_value.raise_for_status = MagicMock()
    mock_session_state["favorites"] = {}

    recipe = {"id": "777", "name": "My super random favorite recipe"}

    result = handle_favorite_click("777", False, recipe)

    assert result is True
    assert "777" in mock_session_state["favorites"]

def test_get_random_recipe(mock_client):
    from src.ui.app import get_random_recipe

    mock_client.return_value.get.return_value.json.return_value = {"id": "789", "name": "Random Recipe mb"}
    mock_client.return_value.get.return_value.raise_for_status = MagicMock()

    recipe = get_random_recipe()

    assert recipe["id"] == "789"
    assert recipe["name"] == "Random Recipe mb"
    mock_client.return_value.get.assert_called_once_with("/recipes/random")

def test_search_recipes(mock_client):
    from src.ui.app import search_recipes

    mock_client.return_value.get.return_value.json.return_value = [
        {"id": "101", "name": "Search Result Recipe"}
    ]
    mock_client.return_value.get.return_value.raise_for_status = MagicMock()

    recipes = search_recipes("test query", "sugar", "salt")

    assert len(recipes) == 1
    assert recipes[0]["id"] == "101"
    assert recipes[0]["name"] == "Search Result Recipe"
    mock_client.return_value.get.assert_called_once_with(
        "/recipes/search",
        params={
            "name": "test query",
            "ingredient": "test query",
            "include_ingredients": "sugar",
            "exclude_ingredients": "salt",
        },
    )

def test_refresh_favorites_error_handling(mock_client, mock_session_state):
    from src.ui.app import refresh_favorites

    mock_client.return_value.get.side_effect = httpx.HTTPError("API Error")

    refresh_favorites()

    assert "favorites" in mock_session_state
    assert mock_session_state["favorites"] == {}

def test_toggle_favorite(mock_client, mock_session_state):
    from src.ui.app import toggle_favorite

    mock_client.return_value.post.return_value.raise_for_status = MagicMock()

    result = toggle_favorite("123")

    assert result is True
    mock_client.return_value.post.assert_called_once_with(
        "/recipes/123/favorite",
        json={"user_id": mock_session_state["user_id"]},
    )

def test_display_recipe_ui(mock_session_state):
    from src.ui.app import display_recipe

    with patch("src.ui.app.st") as mock_st:
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        recipe = {
            "name": "Test Recipe",
            "image_url": "http://example.com/image.jpg",
            "ingredients": ["5 eggs"],
            "instructions": ["Mix ingredients", "fry for 10 minutes over high heat, stirring"],
        }
        display_recipe(recipe)

        mock_st.subheader.assert_called_once_with("Test Recipe")
        mock_st.image.assert_called_once_with("http://example.com/image.jpg", use_container_width=True)
        mock_st.write.assert_any_call("### Ingredients")
        mock_st.write.assert_any_call("- 5 eggs")
        mock_st.write.assert_any_call("### Instructions")
        mock_st.markdown.assert_any_call("1. Mix ingredients")
        mock_st.markdown.assert_any_call("2. fry for 10 minutes over high heat, stirring")

def test_generate_pdf_with_multiple_recipes():
    from src.ui.app import generate_pdf

    recipes = [
        {
            "name": "Recipe 1",
            "ingredients": ["1 cup flour", "2 eggs"],
            "instructions": ["Mix", "Bake"],
            "image_url": "http://example.com/image1.jpg",
        },
        {
            "name": "Recipe 2",
            "ingredients": ["1 cup sugar", "1 cup water"],
            "instructions": ["Boil", "Cool"],
            "image_url": "http://example.com/image2.jpg",
        },
    ]

    pdf_data = generate_pdf(recipes, "Test Recipes")

    assert pdf_data is not None
    assert isinstance(pdf_data, bytes)


def test_main_add_custom_recipe_page(mock_session_state):
    from src.ui.app import main

    with patch("src.ui.app.st") as mock_st:
        mock_st.sidebar.radio.return_value = "Add Custom Recipe"
        mock_st.text_input.side_effect = ["Test Recipe", "http://example.com/image.jpg"]
        mock_st.text_area.side_effect = ["Ingredient 1\nIngredient 2", "Step 1\nStep 2"]
        mock_st.form_submit_button.return_value = True

        main()

        mock_st.header.assert_called_once_with("Add Custom Recipe")
        mock_st.form.assert_called_once_with("custom_recipe_form")
        mock_st.form_submit_button.assert_called_once_with("Add Recipe")

def test_main_random_from_favorites_page(mock_session_state):
    from src.ui.app import main

    with patch("src.ui.app.st") as mock_st:
        mock_st.sidebar.radio.return_value = "Random from Favorites"
        mock_st.button.return_value = True

        main()

        mock_st.header.assert_called_once_with("Random Recipe from Favorites")
        mock_st.button.assert_called_once_with("Get Random Recipe from Favorites")


def test_generate_pdf_with_images():
    from src.ui.app import generate_pdf

    recipes = [
        {
            "name": "Recipe with Image",
            "ingredients": ["1 cup sugar", "2 eggs"],
            "instructions": ["Mix ingredients", "Bake for 20 minutes"],
            "image_url": "http://example.com/image.jpg",
        }
    ]

    pdf_data = generate_pdf(recipes, "Recipes with Images")

    assert pdf_data is not None
    assert isinstance(pdf_data, bytes)

def test_display_recipe_without_image():
    from src.ui.app import display_recipe

    with patch("src.ui.app.st") as mock_st:
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        recipe = {
            "name": "Recipe without Image",
            "ingredients": ["1 cup sugar", "2 eggs"],
            "instructions": ["Mix ingredients", "Bake for 20 minutes"],
        }
        display_recipe(recipe)

        mock_st.subheader.assert_called_once_with("Recipe without Image")
        mock_st.image.assert_not_called()
        mock_st.write.assert_any_call("### Ingredients")
        mock_st.write.assert_any_call("- 1 cup sugar")
        mock_st.write.assert_any_call("- 2 eggs")
        mock_st.write.assert_any_call("### Instructions")
        mock_st.markdown.assert_any_call("1. Mix ingredients")
        mock_st.markdown.assert_any_call("2. Bake for 20 minutes")