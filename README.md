Welcome Our ASL Translating Application
==============================================

What's Here
-----------

This sample includes:

* README.md - this file
* requirements.txt - this file is used install Python dependencies needed by the Flask application
* src/ - contains the source code for the Flask application
* the models/ directory goes in src/. (If available) src/models/ - contains the translation model for the Flask application
* src/templates/ - contains the source code for the html running the Flask application's front end
* src/static/ - contains static files used in the Flask application's front end
* src/*.py - files running our ML system and Flask application's back end

Getting Started
---------------

0. Navigate to project directory
	
	$ cd path/to/asl-fingerspelling-translator/

1. Create a Python virtual environment for the application

        $ python3 -m venv env_name

2. Activate the virtual environment:

        $ source env_name/bin/activate

3. Install Python dependencies for the Flask application:

        $ pip install -r requirements.txt

4. Move into src and export the application file

	$ export FLASK_APP=src/application

5. Start the Flask development server:

        $ flask run

6. Open http://127.0.0.1:5000/ in a web browser to view the output of your
   service.
