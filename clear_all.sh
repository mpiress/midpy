# remove __pycache__ into the project folders 

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
find . | grep -E "(__pycache__(2)|\.pyc|\.pyo$)" | xargs rm -rf
