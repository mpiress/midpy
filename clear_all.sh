# remove __pycache__ into the project folders 

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
