import json
import pprint
import re
import time

import requests
from extruct.jsonld import JsonLdExtractor

pp = pprint.PrettyPrinter(indent=1)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}


def convert_iso_duration_to_human_readable(iso_duration):
    """
    Convert ISO 8601 duration format (e.g., 'PT30M', 'PT1H30M') to human readable format
    """
    if not iso_duration or not isinstance(iso_duration, str):
        return None

    # Remove 'PT' prefix
    duration = iso_duration.replace("PT", "")

    hours = 0
    minutes = 0

    # Extract hours
    hour_match = re.search(r"(\d+)H", duration)
    if hour_match:
        hours = int(hour_match.group(1))

    # Extract minutes
    minute_match = re.search(r"(\d+)M", duration)
    if minute_match:
        minutes = int(minute_match.group(1))

    # Format as human readable
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return None


def extract_webpage_data(url):
    try:
        # Add timeout to prevent hanging (30 seconds total timeout)
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            jslde = JsonLdExtractor()
            data = jslde.extract(response.text)

            # Find the recipe object (usually type "Recipe")
            recipe = None

            for item in data:
                # If the item has an @graph, search inside it, not all JSON-LD formatted the same
                if "@graph" in item:
                    for subitem in item["@graph"]:
                        if "@type" in subitem and (
                            subitem["@type"] == "Recipe"
                            or (
                                isinstance(subitem["@type"], list)
                                and "Recipe" in subitem["@type"]
                            )
                        ):
                            recipe = subitem
                            break
                    if recipe:
                        break
                # Otherwise, check the item itself
                elif "@type" in item and (
                    item["@type"] == "Recipe"
                    or (isinstance(item["@type"], list) and "Recipe" in item["@type"])
                ):
                    recipe = item
                    break

            if recipe:
                if "recipeInstructions" in recipe:
                    print("\nRecipe Instructions:")
                    for instruction in recipe["recipeInstructions"]:
                        # Handle HowToSection (with steps)
                        if (
                            isinstance(instruction, dict)
                            and instruction.get("@type") == "HowToSection"
                        ):

                            section_name = instruction.get("name", "Section")
                            print(f"\n{section_name}:")
                            for step in instruction.get("itemListElement", []):
                                if isinstance(step, dict):

                                    print(
                                        f"  - {step.get('text', step.get('name', str(step)))}"
                                    )
                                else:

                                    print(f"  - {step}")
                        # Handle direct HowToStep
                        elif (
                            isinstance(instruction, dict)
                            and instruction.get("@type") == "HowToStep"
                        ):

                            print(
                                f"- {instruction.get('text', instruction.get('name', str(instruction)))}"
                            )
                        # Handle string steps (rare)
                        elif isinstance(instruction, str):

                            print(f"- {instruction}")
                        else:

                            print(f"- {instruction}")

                if "recipeIngredient" in recipe:
                    print(f"Ingredients: ")
                    for ingredient in recipe["recipeIngredient"]:
                        print(f"    -{ingredient}")

                # Extract cooking times
                if "prepTime" in recipe:
                    recipe["prep_time"] = convert_iso_duration_to_human_readable(
                        recipe["prepTime"]
                    )
                    print(f"Prep Time: {recipe['prep_time']}")

                if "cookTime" in recipe:
                    recipe["cook_time"] = convert_iso_duration_to_human_readable(
                        recipe["cookTime"]
                    )
                    print(f"Cook Time: {recipe['cook_time']}")

                if "totalTime" in recipe:
                    recipe["total_time"] = convert_iso_duration_to_human_readable(
                        recipe["totalTime"]
                    )
                    print(f"Total Time: {recipe['total_time']}")

                return recipe
            else:
                return "No HowToSteps found."
        else:
            return f"Failed to retrieve data. Status code: {response.status_code}"

    except requests.exceptions.Timeout:
        return "Request timed out. The website took too long to respond."
    except requests.exceptions.ConnectionError:
        return "Connection error. Please check the URL and try again."
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
