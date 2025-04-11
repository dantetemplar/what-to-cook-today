from dataclasses import dataclass


@dataclass
class Recipe:
    id: str
    name: str
    image_url: str
    instructions: str
    ingredients: list[str]
    is_favorite: bool = False
    is_custom: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "image_url": self.image_url,
            "instructions": self.instructions,
            "ingredients": self.ingredients,
            "is_favorite": self.is_favorite,
            "is_custom": self.is_custom,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        return cls(
            id=data["id"],
            name=data["name"],
            image_url=data["image_url"],
            instructions=data["instructions"],
            ingredients=data["ingredients"],
            is_favorite=data.get("is_favorite", False),
            is_custom=data.get("is_custom", False),
        )
