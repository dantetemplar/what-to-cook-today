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

- Response time during execution of listed functional requirements ≤ 2 s.
- Response time during API calls ≤ 2 s.

#### Locuts performance report (time in milliseconds):

```log
Response time percentiles (approximated)
Type     Name                                                                             50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|---------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
POST     /recipes/123/favorite                                                              5     13     59     77    120    150    210    230    230    230    230     91
GET      /recipes/custom                                                                    6      7      9     17     84     96    120    600    600    600    600     85
POST     /recipes/custom                                                                    8     10     15     68    110    140    180    180    190    190    190    102
GET      /recipes/favorites                                                                 5      6      8     27    110    170    200    220    600    600    600    114
GET      /recipes/random                                                                  110    120    130    150    200    220    260    330    710    710    710    284
GET      /recipes/search?name=chicken                                                     140    150    170    190    240    260    360    410    600    600    600    184
--------|---------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                                                       110    120    140    140    180    220    260    330    710    710    710    860

```

#### Performance metrics:

- Average response time: 143ms
- 90th percentile response time: 240ms

### Security:

- 0 critical vulnerabilities.
- Fuzzing testing ≥ 80% branch coverage.
