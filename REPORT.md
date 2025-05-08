![CI](https://github.com/dantetemplar/what-to-cook-today/actions/workflows/ci-sonraqube.yml/badge.svg) <- All the test results are here 

# Project Description

"What to cook today" application.

## Functional Requirements:

**Changes in requirements:** We met with the project project manager and agreed on some changes to the project:    
-  Recipes are saved in pdf format after clicking on the download button(offline access to recipes). 
-  Performance requirements have been changed and now we consider request from front end to api and response time should not be more than N ms. 
-  The project does not need to be deployed, the main thing is that the tests can be run locally(or in CI). 


**Initial requirements:**
- Application fetches a list of recipes from an external API ([TheMealDB](https://www.themealdb.com/api.php)) .
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
Passes checks for `ruff` and `flake 8`. 

- Cyclomatic Complexity = A(3.56).
- Code Duplication = 0(no duplicate). 
- Propagation cost = 10/10(cool result).

### Reliability:

- Unit test coverage = 88%. 

### Performance:

- Response time during execution of listed functional requirements ≤ 0.2 ms.
- Response time during API calls ≤ 2 s.

### Security:

- bandit scan: 0 critical vulnerabilities. 
- Fuzzing testing = 99%.
- integrated SonarQube checker. 

### CI 
- https://github.com/dantetemplar/what-to-cook-today/actions/runs/14906248639 - If you want to see all the metrics