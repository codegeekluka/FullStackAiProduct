import re

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database.db_models import Ingredient, Instruction, Recipe, User


def create_user(db: Session, firstname: str, lastname: str, email: str):
    user = User(firstname=firstname, lastname=lastname, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# for development


def delete_all_user_data(db: Session):
    db.execute(text('TRUNCATE TABLE "user" RESTART IDENTITY CASCADE;'))
    db.commit()


# Recipe functions


def create_recipe(db: Session, title: str, user_id: int):
    """
    Create a new recipe for a specific user
    """
    # Generate a simple slug from title
    slug = title.lower().replace(" ", "-").replace("_", "-")
    # Remove any non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    recipe = Recipe(
        title=title,
        slug=slug,
        user_id=user_id,
        description="",
        image="",
        favorite=False,
        is_active=False,
        tags=[],
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def get_recipes_by_user(db: Session, user_id: int):
    """
    Get all recipes for a specific user
    """
    return db.query(Recipe).filter(Recipe.user_id == user_id).all()


def get_recipe_by_id_and_user(db: Session, recipe_id: int, user_id: int):
    """
    Get a specific recipe by its ID, but only if it belongs to the specified user
    """
    return (
        db.query(Recipe)
        .filter(Recipe.id == recipe_id, Recipe.user_id == user_id)
        .first()
    )


# Ingredient functions


def create_ingredient(
    db: Session, name: str, quantity: str, unit: str, recipe_id: int, user_id: int
):
    """
    Create a new ingredient for a specific recipe (only if recipe belongs to user)
    """
    # First verify the recipe belongs to the user
    recipe = get_recipe_by_id_and_user(db, recipe_id, user_id)
    if not recipe:
        raise ValueError("Recipe not found or access denied")

    ingredient = Ingredient(ingredient=f"{quantity} {unit} {name}", recipe_id=recipe_id)
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


def get_all_ingredients_by_recipe_and_user(db: Session, recipe_id: int, user_id: int):
    """
    Get all ingredients for a specific recipe (only if recipe belongs to user)
    """
    return (
        db.query(Ingredient)
        .join(Recipe)
        .filter(Ingredient.recipe_id == recipe_id, Recipe.user_id == user_id)
        .all()
    )


def get_ingredient_by_id_and_user(db: Session, ingredient_id: int, user_id: int):
    """
    Get a specific ingredient by its ID (only if it belongs to user's recipe)
    """
    return (
        db.query(Ingredient)
        .join(Recipe)
        .filter(Ingredient.id == ingredient_id, Recipe.user_id == user_id)
        .first()
    )


def get_all_ingredients_by_user(db: Session, user_id: int):
    """
    Get all ingredients from all recipes of a specific user
    """
    return db.query(Ingredient).join(Recipe).filter(Recipe.user_id == user_id).all()


# Instruction functions


def create_instruction(
    db: Session, step_number: int, description: str, recipe_id: int, user_id: int
):
    """
    Create a new instruction for a specific recipe (only if recipe belongs to user)
    """
    # First verify the recipe belongs to the user
    recipe = get_recipe_by_id_and_user(db, recipe_id, user_id)
    if not recipe:
        raise ValueError("Recipe not found or access denied")

    instruction = Instruction(
        description=description, recipe_id=recipe_id, step_number=step_number
    )
    db.add(instruction)
    db.commit()
    db.refresh(instruction)
    return instruction


def get_all_instructions_by_recipe_and_user(db: Session, recipe_id: int, user_id: int):
    """
    Get all instructions for a specific recipe (only if recipe belongs to user)
    """
    return (
        db.query(Instruction)
        .join(Recipe)
        .filter(Instruction.recipe_id == recipe_id, Recipe.user_id == user_id)
        .order_by(Instruction.step_number)
        .all()
    )


def get_instruction_by_id_and_user(db: Session, instruction_id: int, user_id: int):
    """
    Get a specific instruction by its ID (only if it belongs to user's recipe)
    """
    return (
        db.query(Instruction)
        .join(Recipe)
        .filter(Instruction.id == instruction_id, Recipe.user_id == user_id)
        .first()
    )


def get_all_instructions_by_user(db: Session, user_id: int):
    """
    Get all instructions from all recipes of a specific user
    """
    return (
        db.query(Instruction)
        .join(Recipe)
        .filter(Recipe.user_id == user_id)
        .order_by(Instruction.step_number)
        .all()
    )
