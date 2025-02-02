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

Ensure `PRODUCTION=TRUE` in `/static/vars.py` to load the dataset.

## Connecting To Our Application

Run the following, to see hello world:
`curl -X GET http://localhost:8000`
