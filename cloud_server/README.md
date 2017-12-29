## create database movies_recommendations
use movies_recommendations

## create MongoDB user
db.createUser({"user": "cmpt732", "pwd": "cmpt732", "roles": ["dbOwner"]})

## connection
mongo 199.60.17.175:27017

## import details
mongoimport --db movies_recommendations --collection movie_details --drop --file ~/movie_details.json


