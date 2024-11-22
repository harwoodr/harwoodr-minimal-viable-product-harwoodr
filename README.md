There are two files that represent the two systems of the mvp and both scripts require the pika python module ( https://github.com/pika/pika ) which can be installed via:

pip install pika

entry.py - Gives a command line interface that represents the transponder reader and gate.  It sends permit validation requests to RabbitMQ.
permit.py - Responds to permit validation requests from entry.py (via RabbitMQ)

Run them with your local python 3 (mine is 3.10) in separate terminals.
When running entry.py it simulates the transponder reading function by having the user enter a number from 0-9 where some of the numbers are associated with a permit in the database (a python list for this MVP).

The username and password for RabbitMQ are set to "admin" and "cas735" (respectively) and need to be set in both files if you are not using the docker-compose defined RabbitMQ container.
