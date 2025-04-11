import logging
import uuid

import httpx
import streamlit as st
from streamlit_cookies_controller import CookieController, RemoveEmptyElementContainer

# Set page config first
st.set_page_config(page_title="What to Cook Today", page_icon="🍳", layout="wide")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
API_BASE_URL = "http://localhost:8000"

# Initialize cookie controller
controller = CookieController()
RemoveEmptyElementContainer()


# Initialize httpx client
@st.cache_resource
def get_client():
    return httpx.Client(base_url=API_BASE_URL)


def get_user_id() -> str:
    """Get or create user_id from cookie"""
    # Try to get user_id from session state first
    if "user_id" not in st.session_state:
        # Try to get from cookie
        user_id = controller.get("user_id")
        if not user_id:
            # Generate new user_id if not in cookie
            user_id = str(uuid.uuid4())
            # Set cookie
            controller.set("user_id", user_id)

        st.session_state["user_id"] = user_id
        logger.info(f"Generated new user_id: {user_id}")

    return st.session_state["user_id"]


def get_random_recipe() -> dict | None:
    """Get a random recipe from the API"""
    try:
        response = get_client().get("/recipes/random")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        st.error(f"Error fetching random recipe: {str(e)}")
        return None


def search_recipes(query: str) -> list[dict]:
    """Search recipes by name or ingredient"""
    try:
        response = get_client().get(f"/recipes/search?name={query}&ingredient={query}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        st.error(f"Error searching recipes: {str(e)}")
        return []


def refresh_favorites():
    """Refresh favorites from API"""
    try:
        user_id = get_user_id()
        logger.info(f"Refreshing favorites for user_id: {user_id}")
        response = get_client().get(f"/recipes/favorites?user_id={user_id}")
        response.raise_for_status()
        favorites = response.json()
        logger.info(f"Received {len(favorites)} favorites")
        st.session_state["favorites"] = {recipe["id"]: recipe for recipe in favorites}
    except httpx.HTTPError as e:
        logger.info(f"Error fetching favorite recipes: {str(e)}")
        st.error(f"Error fetching favorite recipes: {str(e)}")
        st.session_state["favorites"] = {}


def get_favorite_recipes() -> list[dict]:
    """Get all favorite recipes for the current user"""
    if "favorites" not in st.session_state:
        logger.info("Favorites not in session state, refreshing")
        refresh_favorites()
    favorites = list(st.session_state["favorites"].values())
    logger.info(f"Returning {len(favorites)} favorites")
    return favorites


def toggle_favorite(recipe_id: str) -> bool:
    """Toggle favorite status for a recipe"""
    try:
        user_id = get_user_id()
        logger.info(f"Toggling favorite for recipe_id: {recipe_id}, user_id: {user_id}")
        logger.info(f"Current favorites before toggle: {list(st.session_state.get('favorites', {}).keys())}")

        # Ensure recipe_id is a string
        recipe_id = str(recipe_id)

        response = get_client().post(f"/recipes/{recipe_id}/favorite", json={"user_id": user_id})
        response.raise_for_status()
        logger.info("Successfully toggled favorite")

        # Refresh favorites after toggling
        refresh_favorites()
        logger.info(f"Favorites after toggle: {list(st.session_state.get('favorites', {}).keys())}")
        return True
    except httpx.HTTPError as e:
        logger.error(f"HTTP error toggling favorite status: {str(e)}")
        st.error(f"Error toggling favorite status: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error toggling favorite status: {str(e)}")
        st.error(f"Error updating favorite status: {str(e)}")
        return False


def is_favorite(recipe_id: str) -> bool:
    """Check if a recipe is favorited"""
    if "favorites" not in st.session_state:
        logger.info("Favorites not in session state, refreshing")
        refresh_favorites()
    is_fav = recipe_id in st.session_state["favorites"]
    logger.info(f"Recipe {recipe_id} is favorited: {is_fav}")
    return is_fav


def add_custom_recipe(recipe: dict) -> bool:
    """Add a custom recipe"""
    try:
        response = get_client().post("/recipes/custom", json=recipe)
        response.raise_for_status()
        return True
    except httpx.HTTPError as e:
        st.error(f"Error adding custom recipe: {str(e)}")
        return False


def handle_favorite_click(recipe_id: str, current_favorite: bool, recipe: dict):
    """Handle favorite button click"""
    logger.info(f"Favorite button clicked for recipe {recipe_id}")
    try:
        if toggle_favorite(recipe_id):
            logger.info("Toggle successful")
            st.success("Favorite status updated!")
            # Update the session state to reflect the change
            if "favorites" not in st.session_state:
                st.session_state["favorites"] = {}

            if current_favorite:
                # Remove from favorites
                if recipe_id in st.session_state["favorites"]:
                    del st.session_state["favorites"][recipe_id]
            else:
                # Add to favorites
                st.session_state["favorites"][recipe_id] = recipe

            logger.info(f"Updated session state favorites: {list(st.session_state['favorites'].keys())}")
            return True
        else:
            logger.info("Toggle failed")
            st.error("Failed to update favorite status")
            return False
    except Exception as e:
        logger.error(f"Error during toggle: {str(e)}")
        st.error(f"Error updating favorite status: {str(e)}")
        return False


def display_recipe(recipe: dict):
    """Display a recipe in a formatted way"""
    st.subheader(recipe.get("name", "Untitled Recipe"))

    # Display image if available
    if recipe.get("image_url"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(recipe["image_url"], use_container_width=True)

    # Display ingredients
    st.write("### Ingredients")
    for ingredient in recipe.get("ingredients", []):
        st.write(f"- {ingredient}")

    # Display instructions
    st.write("### Instructions")
    instructions = recipe.get("instructions", [])

    # Handle different instruction formats
    if isinstance(instructions, str):
        # Split by newlines and clean up
        instructions = [line.strip() for line in instructions.split("\n") if line.strip()]

    # Process and display instructions
    for idx, instruction in enumerate(instructions, 1):
        # Remove "STEP X" prefix if present
        _instruction = instruction.replace("STEP ", "").strip()
        # Remove any leading numbers and dots
        _instruction = _instruction.lstrip("0123456789. ")
        st.markdown(f"{idx}. {_instruction}")

    # Favorite button
    recipe_id = recipe.get("id")
    if recipe_id:
        current_favorite = is_favorite(recipe_id)
        logger.info(f"Displaying recipe {recipe_id}, current favorite status: {current_favorite}")

        # Create a container for the button to ensure it's always rendered
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                button_text = "❤️ Remove from Favorites" if current_favorite else "🤍 Add to Favorites"
                if st.button(button_text, key=f"fav_{recipe_id}"):
                    handle_favorite_click(recipe_id, current_favorite, recipe)


def main():
    st.title("🍳 What to Cook Today")

    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["Home", "Search Recipes", "Favorites", "Add Custom Recipe"])

    if page == "Home":
        st.header("Random Recipe Suggestion")

        # Initialize random recipe in session state if not exists
        if "random_recipe" not in st.session_state:
            st.session_state.random_recipe = None

        # Get new random recipe button
        if st.button("Get Random Recipe"):
            recipe = get_random_recipe()
            if recipe:
                st.session_state.random_recipe = recipe

        # Display current random recipe if exists
        if st.session_state.random_recipe:
            display_recipe(st.session_state.random_recipe)

    elif page == "Search Recipes":
        st.header("Search Recipes")
        search_query = st.text_input("Search by name or ingredient")
        if search_query:
            recipes = search_recipes(search_query)
            if recipes:
                for recipe in recipes:
                    display_recipe(recipe)
            else:
                st.info("No recipes found matching your search.")

    elif page == "Favorites":
        st.header("Favorite Recipes")
        favorites = get_favorite_recipes()
        if favorites:
            for recipe in favorites:
                display_recipe(recipe)
        else:
            st.info("You haven't favorited any recipes yet.")

    elif page == "Add Custom Recipe":
        st.header("Add Custom Recipe")
        with st.form("custom_recipe_form"):
            name = st.text_input("Recipe Name")
            ingredients = st.text_area("Ingredients (one per line)")
            instructions = st.text_area("Instructions (one step per line)")
            image_url = st.text_input("Image URL (optional)")

            submitted = st.form_submit_button("Add Recipe")
            if submitted:
                recipe = {
                    "name": name,
                    "ingredients": [i.strip() for i in ingredients.split("\n") if i.strip()],
                    "instructions": [i.strip() for i in instructions.split("\n") if i.strip()],
                    "image_url": image_url if image_url else None,
                }
                if add_custom_recipe(recipe):
                    st.success("Recipe added successfully!")
                else:
                    st.error("Failed to add recipe.")


if __name__ == "__main__":
    main()
