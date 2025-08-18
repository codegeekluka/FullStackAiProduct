from fastapi import  APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from fastapi.responses import JSONResponse
from backend.database.database import get_db
from backend.database.db_models import Recipe, Instruction, Ingredient, User, Tag
from pydantic import BaseModel
from backend.Scrapers.scraper import extract_webpage_data
from backend.Apis.auth import get_current_user
from backend.services.ai_assistant import ai_assistant
import re
from typing import List, Optional
import traceback
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor


#creates new router instance
router = APIRouter()

class RecipeRequest(BaseModel):
    url: str
class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    ingredients: Optional[List[str]] = None
    instructions: Optional[List[str]] = None
    is_active: Optional[bool] = False
    favorite: Optional[bool] = False
    tags: Optional[List[str]] = None

class TagsUpdate(BaseModel):
    tags: List[str]

def generate_unique_slug(db: Session, title: str) -> str:
    base_slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    slug = base_slug
    count = 1

    while db.query(Recipe).filter(Recipe.slug == slug).first() is not None:
        slug = f"{base_slug}-{count}"
        count += 1

    return slug


def extract_instruction_texts(instructions):
    steps = []

    if isinstance(instructions, str):
        return [instructions]

    for item in instructions:
        if isinstance(item, dict):
            item_type = item.get("@type")

            if item_type == "HowToSection":
                section_name = item.get("name")
                if section_name:
                    steps.append(f"## {section_name}")  # Markdown-style header, or just plain text
                section_items = item.get("itemListElement", [])
                steps.extend(extract_instruction_texts(section_items))

            elif item_type == "HowToStep":
                text = item.get("text")
                if text:
                    steps.append(text)

        elif isinstance(item, str):
            steps.append(item)

    return steps

#when defining endpoints, FastAPI app must be ware of these
@router.post('/RecipePage')
def parse_recipe(req: RecipeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        recipe = extract_webpage_data(req.url)
        
        # Check for specific error messages from the scraper
        if isinstance(recipe, str):
            if recipe == 'No HowToSteps found.':
                raise ValueError("No recipe found on this page. Please check if the URL contains a recipe.")
            elif recipe == "Failed to retrieve data.":
                raise ValueError("Failed to access the website. Please check the URL and try again.")
            elif "timed out" in recipe.lower():
                raise ValueError("The website took too long to respond. Please try again later.")
            elif "connection error" in recipe.lower():
                raise ValueError("Connection error. Please check your internet connection and try again.")
            elif "request failed" in recipe.lower():
                raise ValueError("Failed to access the website. The site may be blocking automated requests.")
            elif "unexpected error" in recipe.lower():
                raise ValueError("An unexpected error occurred while scraping. Please try again.")
            else:
                raise ValueError(f"Scraping failed: {recipe}")
        
        # Validate that we have the required recipe data
        if not isinstance(recipe, dict) or "name" not in recipe:
            raise ValueError("Invalid recipe data received from the website.")
            
        # Create and store recipe
        slug = generate_unique_slug(db, recipe["name"])

        image_data = recipe.get("image", "")
        # If it's a dict (like ImageObject), extract the 'url' key
        if isinstance(image_data, dict):
            image = image_data.get("url", "")
        # If it's a list of images, use the first one
        elif isinstance(image_data, list) and image_data:
            first = image_data[0]
            image = first.get("url", "") if isinstance(first, dict) else first
        # If it's already a string, use it directly
        elif isinstance(image_data, str):
            image = image_data
        else:
            image = ""

        new_recipe = Recipe(
            title=recipe["name"],
            slug=slug,
            user_id=current_user.id,
            description=recipe.get("description", ""),
            image=image,
            favorite=False,
            is_active=False,
            tags=[]
            )
        db.add(new_recipe)
        db.flush()  # Assigns recipe.id

        # Add instructions (handle string list or object format)
        instructions = recipe.get("recipeInstructions", [])
        step_texts = extract_instruction_texts(instructions)

        for i, step_text in enumerate(step_texts):
            db.add(Instruction(description=step_text, recipe_id=new_recipe.id, step_number=i+1))
        if not step_texts:
            raise ValueError("No valid instructions found in the recipe. Please try a different recipe URL.")

        # Add ingredients
        ingredients = recipe.get("recipeIngredient", [])
        if not ingredients:
            raise ValueError("No ingredients found in the recipe. Please try a different recipe URL.")
            
        for item in ingredients:
            db.add(Ingredient(ingredient=item, recipe_id=new_recipe.id))

        db.commit()
        
        # Generate embeddings asynchronously in the background
        def generate_embeddings_async():
            try:
                # Create a new database session for the background task
                from backend.database.database import SessionLocal
                background_db = SessionLocal()
                try:
                    ai_assistant.update_recipe_embeddings(background_db, new_recipe.id)
                    print(f"Successfully generated embeddings for recipe {new_recipe.id}")
                finally:
                    background_db.close()
            except Exception as e:
                print(f"Warning: Failed to generate embeddings for recipe {new_recipe.id}: {e}")
        
        # Start embeddings generation in a background thread
        threading.Thread(target=generate_embeddings_async, daemon=True).start()
        
        return {"recipe_id": new_recipe.id, "slug": slug} #return on success
        
    except ValueError as e:
        # Re-raise ValueError with the specific error message
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error during recipe parsing: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")

@router.get("/recipes/{slug}")
def get_recipe_by_slug(slug: str, db: Session = Depends(get_db)):
    #joinedload eager loads tags
    recipe = db.query(Recipe).options(joinedload(Recipe.tags)).filter(Recipe.slug == slug).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    ingredients = db.query(Ingredient).filter(Ingredient.recipe_id == recipe.id).all()
    instructions = db.query(Instruction).filter(Instruction.recipe_id == recipe.id).all()

    return {
        "title": recipe.title,
        "slug": recipe.slug,
        "description": recipe.description,
        "image": recipe.image,
        "ingredients": [i.ingredient for i in ingredients],
        "instructions": [step.description for step in instructions],
        "is_favorite": recipe.favorite,
        "is_active": recipe.is_active,
        "tags": [tag.name for tag in recipe.tags]
    }

@router.get("/user/recipes")
def get_user_recipes(current_user: User = Depends(get_current_user), db: Session= Depends(get_db)):
    try: 
        user_recipes= db.query(Recipe).filter(Recipe.user_id == current_user.id).all()
        return {"recipes": [recipe.to_dict() for recipe in user_recipes]}
    except Exception as e:
        print("Error fetching recipes: ", e)
        return JSONResponse(status_code=500, content={"detail": "Server error"})
  

#Updating Recipe information:
@router.put("/recipes/{slug}")
def update_recipe(
    slug: str,
    updated_data: RecipeUpdate,  # Expect title, description, ingredients, instructions
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    db_recipe = db.query(Recipe).filter(Recipe.slug == slug).first()

    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if db_recipe.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to edit this recipe")

     # Update only provided fields
    if updated_data.title is not None:
        db_recipe.title = updated_data.title
    if updated_data.description is not None:
        db_recipe.description = updated_data.description

    if updated_data.ingredients is not None:
        db.query(Ingredient).filter(Ingredient.recipe_id == db_recipe.id).delete()
        for item in updated_data.ingredients:
            db.add(Ingredient(recipe_id=db_recipe.id, ingredient=item))

    if updated_data.instructions is not None:
        db.query(Instruction).filter(Instruction.recipe_id == db_recipe.id).delete()
        for i, step in enumerate(updated_data.instructions):
            db.add(Instruction(recipe_id=db_recipe.id, description=step, step_number=i+1))

    db.commit()
    db.refresh(db_recipe)
    
    # Update embeddings for the modified recipe asynchronously
    def update_embeddings_async():
        try:
            # Create a new database session for the background task
            from backend.database.database import SessionLocal
            background_db = SessionLocal()
            try:
                ai_assistant.update_recipe_embeddings(background_db, db_recipe.id)
                print(f"Successfully updated embeddings for recipe {db_recipe.id}")
            finally:
                background_db.close()
        except Exception as e:
            print(f"Warning: Failed to update embeddings for recipe {db_recipe.id}: {e}")
    
    # Start embeddings generation in a background thread
    threading.Thread(target=update_embeddings_async, daemon=True).start()

    return db_recipe

#delete recipe

@router.delete("/recipes/{slug}", status_code=204)
def delete_recipe(slug: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_recipe = db.query(Recipe).filter(Recipe.slug == slug).first()

    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if db_recipe.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this recipe")

    # Delete related ingredients and instructions first (if needed)
    db.query(Ingredient).filter(Ingredient.recipe_id == db_recipe.id).delete()
    db.query(Instruction).filter(Instruction.recipe_id == db_recipe.id).delete()

    # Then delete the recipe itself
    db.delete(db_recipe)
    db.commit()

    return {"detail": "Recipe deleted"}

#Add recipe manually:
@router.post("/recipe/manualRecipe")
def create_manual_recipe(
    recipe_in: RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("Received recipe_in:", recipe_in.dict())

    try:
        # Generate a unique slug
        slug = generate_unique_slug(db, recipe_in.title)
        # Create and store the main recipe
        new_recipe = Recipe(
            title=recipe_in.title,
            slug=slug,
            user_id=current_user.id,
            description=recipe_in.description,
            image=recipe_in.image,
            favorite=recipe_in.favorite if recipe_in.favorite is not None else False,
            is_active=recipe_in.is_active if recipe_in.is_active is not None else False,
            tags=[]
        )
        db.add(new_recipe)
        db.flush()  # Assigns new_recipe.id

        # Add ingredients
        for item in recipe_in.ingredients:
            db.add(Ingredient(ingredient=item, recipe_id=new_recipe.id))

        # Add instructions
        for i, step_text in enumerate(recipe_in.instructions):
            db.add(Instruction(description=step_text, recipe_id=new_recipe.id, step_number=i+1))
        # Tags
        if recipe_in.tags:
            for tag_name in recipe_in.tags:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.flush()  # get tag.id assigned
                new_recipe.tags.append(tag)  # link tag with recipe

        db.commit()
        
        # Generate embeddings for the new recipe asynchronously
        def generate_embeddings_async():
            try:
                # Create a new database session for the background task
                from backend.database.database import SessionLocal
                background_db = SessionLocal()
                try:
                    ai_assistant.update_recipe_embeddings(background_db, new_recipe.id)
                    print(f"Successfully generated embeddings for manual recipe {new_recipe.id}")
                finally:
                    background_db.close()
            except Exception as e:
                print(f"Warning: Failed to generate embeddings for manual recipe {new_recipe.id}: {e}")
        
        # Start embeddings generation in a background thread
        threading.Thread(target=generate_embeddings_async, daemon=True).start()

        return {"recipe_id": new_recipe.id, "slug": slug}

    except Exception as e:
        db.rollback()
        print("Error creating recipe:", str(e))
        print(traceback.format_exc())

        raise HTTPException(status_code=500, detail=f"Failed to create recipe: {str(e)}")


@router.put("/recipe/{slug}/favorite")
def toggle_favorite(slug: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    print(f"hello")
    recipe = db.query(Recipe).filter(Recipe.slug == slug).first()
    print(recipe)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    recipe.favorite = not recipe.favorite
    db.commit()
    db.refresh(recipe)
    return {"slug": slug, "is_favorite": recipe.favorite}

@router.put("/recipe/{slug}/active")
def toggle_active(slug: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    recipe = db.query(Recipe).filter(Recipe.slug == slug).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # If we're activating this recipe, deactivate all other recipes first
    if not recipe.is_active:
        # Deactivate all other recipes for this user
        db.query(Recipe).filter(
            Recipe.user_id == user.id,
            Recipe.is_active == True
        ).update({"is_active": False})
    
    # Toggle the current recipe's active status
    recipe.is_active = not recipe.is_active
    db.commit()
    db.refresh(recipe)
    return {"slug": slug, "is_active": recipe.is_active}


@router.put("/recipe/{slug}/tags")
def add_tags(slug: str, tag_names: TagsUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    recipe = db.query(Recipe).filter(Recipe.slug == slug).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    for name in tag_names.tags:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()

        if tag not in recipe.tags:
            recipe.tags.append(tag)

    db.commit()
    db.refresh(recipe)
    return {"slug": slug, "tags": [t.name for t in recipe.tags]}

@router.get("/user/active-recipe")
def get_active_recipe(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the currently active recipe for the user"""
    try:
        active_recipe = db.query(Recipe).filter(
            Recipe.user_id == current_user.id,
            Recipe.is_active == True
        ).first()
        
        if not active_recipe:
            return {"active_recipe": None}
        
        # Get ingredients and instructions
        ingredients = db.query(Ingredient).filter(Ingredient.recipe_id == active_recipe.id).all()
        instructions = db.query(Instruction).filter(Instruction.recipe_id == active_recipe.id).all()
        
        return {
            "active_recipe": {
                "id": active_recipe.id,
                "title": active_recipe.title,
                "slug": active_recipe.slug,
                "description": active_recipe.description,
                "image": active_recipe.image,
                "ingredients": [i.ingredient for i in ingredients],
                "instructions": [step.description for step in instructions],
                "tags": [tag.name for tag in active_recipe.tags]
            }
        }
    except Exception as e:
        print("Error fetching active recipe: ", e)
        return JSONResponse(status_code=500, content={"detail": "Server error"})

