# Sojourn
Platform for sharing your vacation home with friends and family

## Installation (Ubuntu)
- sudo apt-get install postgresql postgresql-contrib
- createdb book_app
- python3 -m venv env
- source env/bin/activate
- pip install -r requirements.txt
- export FLASK_APP=app
- export FLASK_ENV=development
- flask init-db
- Then create an env.sh file with the following lines:
  - export FLASK_SECRET_KEY=(random and secure string)
  - export FLASK_SECURITY_PASSWORD_SALT=(random and secure string)
  - export AWS_SES_ACCESS_KEY_ID=(AWS access key for sending emails)
  - export AWS_SES_SECRET_ACCESS_KEY=(AWS secret key for sending emails)
  - export FLASK_ENV=development
- source env.sh
- flask run
