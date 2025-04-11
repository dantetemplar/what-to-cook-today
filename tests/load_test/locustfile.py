from locust import HttpUser, task, between

class RecipeUser(HttpUser):
    wait_time = between(1, 3)  # Wait between 1 and 3 seconds between tasks

    @task(3)
    def get_random_recipe(self):
        self.client.get("/recipes/random")

    @task(2)
    def search_recipes(self):
        self.client.get("/recipes/search?name=chicken")

    @task(1)
    def get_favorites(self):
        self.client.get("/recipes/favorites")

    @task(1)
    def get_custom_recipes(self):
        self.client.get("/recipes/custom")

    @task(1)
    def toggle_favorite(self):
        self.client.post("/recipes/123/favorite")

    @task(1)
    def add_custom_recipe(self):
        self.client.post(
            "/recipes/custom",
            json={
                "id": "123",
                "name": "Custom Recipe",
                "image_url": "http://example.com/image.jpg",
                "instructions": "Test instructions",
                "ingredients": ["ingredient1", "ingredient2"],
                "is_favorite": False,
                "is_custom": True,
            }
        ) 