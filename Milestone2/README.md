  # CS-348

  ## Setup Instructions
  1.	Install Prerequisites:
    •	Docker
    •	Make

  2.	Run the App:
    •	Navigate to the `Milestone1` folder:
          `cd Milestone1`
      •	Start the application:
          `make start`
      
  And the fastapi server along with postgres should be running! You should also be able to see the initially seeded data that we've
  take from Maven Analytics.

  For each of the 4 milestones, we plan to just copy over the code from the previous milestone and duplicate the code.


  ## Seeding Data

  Ensure `PRODUCTION=TRUE` in `/static/vars.py` to load the entire dataset.

  ## Connecting To Our Application

  Run the following, to see hello world:
  `curl -X GET http://localhost:8000`

  ## Features

  - Searching our database of movies (http://localhost:8000/movies/)
      - supports filtering by:
        - title
        - genres
        - actors
        - directors
        - writers
        - studios
      - curl: `curl http://localhost:8000/movies/search?actors=Tom Hanks&studios=Sony Pictures&genres=Drama&genres=Action %26 Adventure`
  - CRUD operations on movies (http://localhost:8000/movies)

  - Create a New Movie
    To add a new movie, send a `POST` request:
```sh
curl -X POST "http://localhost:8000/movies/" \
-H "Content-Type: application/json" \
-d '{
    "title": "New Movie",
    "info": "A great new movie",
    "rating": "PG-13",
    "genres": ["Action", "Adventure"],
    "directors": ["John Doe"],
    "actors": ["Jane Smith", "Bob Wilson"],
    "studios": ["Universal"]
}'
```

  - Retrieve a Movie
    To fetch details of a specific movie by ID:
```sh
curl "http://localhost:8000/movies/1"
```

  - Update a Movie
    To modify an existing movie, send a PUT request with updated fields:
```sh
curl -X PUT "http://localhost:8000/movies/1" \
-H "Content-Type: application/json" \
-d '{
    "title": "Updated Movie Title",
    "genres": ["Comedy"],
    "actors": ["New Actor"]
}'
```

  - Delete a Movie
    To remove a movie by ID:
```sh
curl -X DELETE "http://localhost:8000/movies/1"
```
