import logging
import uuid

import httpx
import streamlit as st
from fpdf import FPDF
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


def search_recipes(
    query: str, include_ingredients: str | None = None, exclude_ingredients: str | None = None
) -> list[dict]:
    """Search recipes by name or ingredient with optional ingredient filtering"""
    try:
        params = {
            "name": query,
            "ingredient": query,
            "include_ingredients": include_ingredients,
            "exclude_ingredients": exclude_ingredients,
        }
        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}

        response = get_client().get("/recipes/search", params=params)
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


def generate_pdf(recipes: list[dict], title: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Courier", size=12)

    pdf.set_font("Courier", style="B", size=18) # Title font
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)

    for recipe in recipes:
        pdf.set_font("Courier", style="B", size=14)
        pdf.cell(0, 10, txt=recipe.get("name", "Untitled Recipe"), ln=True, align='L')
        pdf.ln(5)

        image_url = recipe.get("image_url")
        if image_url:
            try:
                response = httpx.get(image_url)
                response.raise_for_status()
                temp_image_path = f"temp_image_{recipe.get('id', 'unknown')}.jpg"

                with open(temp_image_path, "wb") as img_file:
                    img_file.write(response.content)

                current_y = pdf.get_y()
                pdf.image(temp_image_path, x=10, y=current_y, w=100)
                pdf.set_y(current_y + 70) 
                pdf.ln(30)

            except Exception as e:
                pdf.set_font("Arial", size=10)
                pdf.cell(0, 10, txt=f"[Image could not be loaded: {str(e)}]", ln=True)
                pdf.ln(5)

        # ingredients section
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, txt="Ingredients:", ln=True)
        pdf.set_font("Arial", size=12)
        for ingredient in recipe.get("ingredients", []):
            pdf.cell(0, 10, txt=f"- {ingredient}", ln=True)
        pdf.ln(5)

        # instructions section
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, txt="Instructions:", ln=True)
        pdf.set_font("Arial", size=12)
        instructions = recipe.get("instructions", [])
        if isinstance(instructions, str):
            instructions = [line.strip() for line in instructions.split("\n") if line.strip()]
        for idx, instruction in enumerate(instructions, 1):
            pdf.multi_cell(0, 10, txt=f"{idx}. {instruction}")
        pdf.ln(10)

        # separator between recipes
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

    return pdf.output(dest='S').encode('latin1') # save pdf


def get_random_recipe_from_favorites():
    user_id = get_user_id()
    try:
        response = get_client().get(f"/recipes/random_from_favorites?user_id={user_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        st.error(f"Failed to fetch a random recipe from favorites: {str(e)}")
        return None


def get_random_recipe_from_custom():
    user_id = get_user_id()
    try:
        response = get_client().get(f"/recipes/random_from_custom?user_id={user_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        st.error(f"Failed to fetch a random recipe from custom recipes: {str(e)}")
        return None


def main():
    st.title("🍳 What to Cook Today")

    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["Home", "Search Recipes", "Custom Recipes", "Add Custom Recipe", "Random from Favorites", "Random from Custom", "Favorites"])

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
        st.info("You can search by recipe name, ingredient, or filter by ingredients only")
        search_query = st.text_input(
            "Search by name or ingredient (optional)", help="Leave empty to search by ingredients only"
        )

        # Add ingredient filtering controls
        col1, col2 = st.columns(2)
        with col1:
            include_ingredients = st.text_input(
                "Include ingredients (comma-separated)",
                help="Show recipes that contain ANY of these ingredients (measurements like '100g' or '2 cups' are ignored)",
            )
        with col2:
            exclude_ingredients = st.text_input(
                "Exclude ingredients (comma-separated)",
                help="Hide recipes that contain ANY of these ingredients (measurements like '100g' or '2 cups' are ignored)",
            )

        # Search when either search_query or include_ingredients is provided
        if search_query or include_ingredients:
            recipes = search_recipes(search_query, include_ingredients, exclude_ingredients)
            if recipes:
                for recipe in recipes:
                    display_recipe(recipe)
            else:
                st.info("No recipes found matching your search criteria.")

    elif page == "Favorites":
        st.header("Favorite Recipes")
        favorites = get_favorite_recipes()
        if favorites:
            if st.button("I want to download the recipes"):
                pdf_data = generate_pdf(favorites, "Favorite Recipes")
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name="favorite_recipes.pdf",
                    mime="application/pdf"
                )
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
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "ingredients": [i.strip() for i in ingredients.split("\n") if i.strip()],
                    "instructions": "\n".join([i.strip() for i in instructions.split("\n") if i.strip()]),
                    "image_url": image_url if image_url else None,
                    "is_favorite": False,
                    "is_custom": True
                }
                if add_custom_recipe(recipe):
                    st.success("Recipe added successfully!")
                else:
                    st.error("Failed to add recipe.")

    elif page == "Random from Favorites":
        st.header("Random Recipe from Favorites")

        if "random_favorite_recipe" not in st.session_state:
            st.session_state.random_favorite_recipe = None

        if st.button("Get Random Recipe from Favorites"):
            recipe = get_random_recipe_from_favorites()
            if recipe:
                st.session_state.random_favorite_recipe = recipe
            else:
                st.warning("The favorites list is empty.")

        if st.session_state.random_favorite_recipe:
            display_recipe(st.session_state.random_favorite_recipe)

    elif page == "Random from Custom":
        st.header("Random Recipe from Custom Recipes")

        if "random_custom_recipe" not in st.session_state:
            st.session_state.random_custom_recipe = None

        if st.button("Get Random Recipe from Custom"):
            recipe = get_random_recipe_from_custom()
            if recipe:
                st.session_state.random_custom_recipe = recipe
            else:
                st.warning("The favorites list is empty.")

        if st.session_state.random_custom_recipe:
            display_recipe(st.session_state.random_custom_recipe)

    elif page == "Custom Recipes":
        st.header("Custom Recipes")

        try:
            response = get_client().get("/recipes/custom")
            response.raise_for_status()
            custom_recipes = response.json()

            if custom_recipes:
                if st.button("I want to download the recipes"):
                    pdf_data = generate_pdf(custom_recipes, "Custom Recipes")
                    st.download_button(
                        label="Download PDF",
                        data=pdf_data,
                        file_name="custom_recipes.pdf",
                        mime="application/pdf"
                    )
                for recipe in custom_recipes:
                    display_recipe(recipe)
            else:
                st.info("No custom recipes found.")

        except httpx.HTTPError as e:
            st.error(f"Error fetching custom recipes: {str(e)}")


if __name__ == "__main__":
    main()