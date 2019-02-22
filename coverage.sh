cd ~/fortnite
coverage run -m pytest
coverage html -d ~/fortnite/coverage_html
coverage report
