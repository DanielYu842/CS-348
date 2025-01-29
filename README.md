# CS-348

## Setup Instructions
1.	Install Prerequisites:
	•	Docker
	•	Make

2.	Run the App:
	•	Navigate to the `Milestone0` folder:
        `cd Milestone0`
    •	Start the application:
        `make start`
    
And the fastapi server along with postgres should be running!

For each of the 4 milestones, we plan to just copy over the code from the previous milestone and duplicate the code.


## Seeding Data

`cd Milestone0`
`./setup_and_seed.sh`

## Connecting To Our Application

Run the following, to see hello world:
`curl -X GET http://localhost:8000`