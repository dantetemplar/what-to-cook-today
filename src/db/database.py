import sqlite3

from ..models.recipe import Recipe


class Database:
    def __init__(self, db_path: str = "recipes.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Create recipes table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS recipes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    image_url TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    is_custom INTEGER DEFAULT 0
                )
                """
            )
            # Create favorites table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS favorites (
                    user_id TEXT NOT NULL,
                    recipe_id TEXT NOT NULL,
                    PRIMARY KEY (user_id, recipe_id),
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
                )
                """
            )
            conn.commit()

    def add_recipe(self, recipe: Recipe) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO recipes 
                (id, name, image_url, instructions, ingredients, is_custom)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    recipe.id,
                    recipe.name,
                    recipe.image_url,
                    recipe.instructions,
                    ",".join(recipe.ingredients),
                    int(recipe.is_custom),
                ),
            )
            conn.commit()

    def get_recipe(self, recipe_id: str) -> Recipe | None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
            row = cursor.fetchone()
            if row:
                return Recipe(
                    id=row[0],
                    name=row[1],
                    image_url=row[2],
                    instructions=row[3],
                    ingredients=row[4].split(","),
                    is_favorite=False,  # This will be determined by the favorites table
                    is_custom=bool(row[5]),
                )
            return None

    def get_all_recipes(self) -> list[Recipe]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes")
            return [
                Recipe(
                    id=row[0],
                    name=row[1],
                    image_url=row[2],
                    instructions=row[3],
                    ingredients=row[4].split(","),
                    is_favorite=False,  # This will be determined by the favorites table
                    is_custom=bool(row[5]),
                )
                for row in cursor.fetchall()
            ]

    def get_favorite_recipes(self, user_id: str) -> list[Recipe]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT r.*, 1 as is_favorite
                FROM recipes r
                JOIN favorites f ON r.id = f.recipe_id
                WHERE f.user_id = ?
                """,
                (user_id,),
            )
            return [
                Recipe(
                    id=row[0],
                    name=row[1],
                    image_url=row[2],
                    instructions=row[3],
                    ingredients=row[4].split(","),
                    is_favorite=True,
                    is_custom=bool(row[5]),
                )
                for row in cursor.fetchall()
            ]

    def get_custom_recipes(self) -> list[Recipe]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes WHERE is_custom = 1")
            return [
                Recipe(
                    id=row[0],
                    name=row[1],
                    image_url=row[2],
                    instructions=row[3],
                    ingredients=row[4].split(","),
                    is_favorite=False,  # This will be determined by the favorites table
                    is_custom=bool(row[5]),
                )
                for row in cursor.fetchall()
            ]

    def toggle_favorite(self, recipe_id: str, user_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Check if recipe exists
            cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipe_id,))
            if not cursor.fetchone():
                return False

            # Check if already favorited
            cursor.execute(
                "SELECT 1 FROM favorites WHERE user_id = ? AND recipe_id = ?",
                (user_id, recipe_id),
            )
            if cursor.fetchone():
                # Remove from favorites
                cursor.execute(
                    "DELETE FROM favorites WHERE user_id = ? AND recipe_id = ?",
                    (user_id, recipe_id),
                )
            else:
                # Add to favorites
                cursor.execute(
                    "INSERT INTO favorites (user_id, recipe_id) VALUES (?, ?)",
                    (user_id, recipe_id),
                )
            conn.commit()
            return True
