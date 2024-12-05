from ._abstract import AbstractScraper
import re
from ._exceptions import FieldNotProvidedByWebsiteException
from ._utils import normalize_string

class IrishCentral(AbstractScraper):
    @classmethod
    def host(cls):
        return "irishcentral.com"

    def author(self):
        author_element = self.soup.find("div", class_="article-header-byline-author")
        return author_element.get_text(strip=True)

    def description(self):
        description = self.soup.find("meta", {"property": "og:description"})["content"]
        return description

    def image(self):
        return self.schema.image()

    def ingredients(self):
        # Check if the ingredients are in a <p> structure (https://www.irishcentral.com/culture/food-drink/apple-jameson-tart-recipe)
        ingredients_label = self.soup.find("p", string=re.compile(r"Ingredients:"))

        if ingredients_label:
            ingredients_list = []
            ingredients_paragraphs = ingredients_label.find_next_siblings("p")

            for paragraph in ingredients_paragraphs:
                text = normalize_string(paragraph.get_text())

                if not text or text.lower() in ["most read", "popular"]:
                    continue

                if not text.startswith("-") and not any(char.isdigit() for char in text):
                    break

                ingredients_list.append(text.lstrip("-").strip())

            if ingredients_list:
                return ingredients_list

            # Check if the ingredients are in a <ul> structure (https://www.irishcentral.com/culture/food-drink/shepherds-pie-recipe)
            ingredients_list = ingredients_label.find_next("ul")
            if ingredients_list:
                ingredients_list = [
                    normalize_string(li.get_text())
                    for li in ingredients_list.find_all("li")
                    if li.get_text(strip=True) and li.get_text(strip=True).lower() not in ["most read", "popular"]
                ]
                if ingredients_list:
                    return ingredients_list

        return FieldNotProvidedByWebsiteException(return_value=None)

    def instructions(self):
        instructions_label = self.soup.find("p", text=re.compile(r"Method:"))

        if instructions_label:
            instructions_list = []
            instructions_steps = instructions_label.find_next_siblings("p")

            for step in instructions_steps:
                instruction_text = normalize_string(step.get_text())

                if not instruction_text or instruction_text.startswith("*"):
                    break

                instructions_list.append(instruction_text)

            if not instructions_list:
                return FieldNotProvidedByWebsiteException(return_value=None)

            return "\n".join(instructions_list)

        return FieldNotProvidedByWebsiteException(return_value=None)

    def title(self):
        title = self.soup.find('meta', {'property': 'og:title'})['content']
        return title if title else FieldNotProvidedByWebsiteException(return_value=None)

    def total_time(self):
        return FieldNotProvidedByWebsiteException(return_value=None)

    def yields(self):
        serves_label = self.soup.find("strong", text=lambda t: t and "Serves:" in t)

        if serves_label:
            serves_text = normalize_string(serves_label.get_text())
            serves_value = serves_text.replace("Serves:", "").strip()
            return f"Serves {serves_value}"

        raise FieldNotProvidedByWebsiteException(return_value=None)

    def keywords(self):
        keywords = self.soup.find('meta', {'name': 'keywords'})['content']
        if keywords:
            return [keyword.strip() for keyword in keywords.split(',')]
        else:
            raise FieldNotProvidedByWebsiteException(return_value=None)
