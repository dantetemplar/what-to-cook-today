# Project Description

"What to cook today" application.

## Functional Requirements:

- Application fetches a list of recipes from an external API ([TheMealDB](https://www.themealdb.com/api.php) is suggested. Alternatives may be discussed with the PM).
- Recipes list can be either fetched each time or fetched once in a certain interval and then stored locally on the user device.
- User uses this app to get a random recipe out of the fetched list.
- User may also browse the whole list of recipes.
- Before getting the recipe, user may filter the search by including/excluding certain ingredients.
- User may add favorite recipes to "Favorites" list.
- Recipes from the "Favorites" list are always stored locally on the user device and are available offline.
- User may add their own recipes to the "Custom" list. These recipes are not uploaded anywhere and are saved only on the user device.
- Both "Favorites" and "Custom" lists can be used for a random recipe selection.
- Recipes are represented with the dish name, image, and steps required to cook it.

## Quality Requirements:

Maintainability, Reliability, and Security metrics must be tested with SonarQube integrated into the CI/CD pipeline.

### Maintainability:

- Cyclomatic Complexity ≤ 20 per function/method.
- Code Duplication ≤ 5%.
- Propagation cost ≤ 15%.

### Reliability:

- Unit test coverage ≥ 65%.

### Performance:

- Response time during execution of listed functional requirements ≤ 0.2 ms.
- Response time during API calls ≤ 2 s.

### Security:

- 0 critical vulnerabilities.
- Fuzzing testing ≥ 80% branch coverage.
