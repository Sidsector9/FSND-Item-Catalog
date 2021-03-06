# Items Catalog
## Project
A simple Flask and Python-based website to display a list of Sports Items by Sports Category.

_**Note:**_ Visit http://localhost:5000 instead of http://0.0.0.0:5000 for Google Sign-In to work.

## Database Schema
For simplicity, this website contains 2 relations: **Catalog** and **Items**.

### Catalog
| name | bio | id |
|------|-----|----|

### Items
| id | category_id | name | slug | description | user_email |
|----|-------------|------|------|-------------|------------|

`category_id` is the foreign key on `catalog.id`

_**Note:**_ There is not dedicated relation to store User data since there is no requirement to pull Items data by User.

## Requirements
- Python 2.7.12

This app requires the [slugify](https://github.com/un33k/python-slugify) module to generate slugs.

As per the requirements, the items are queried by the URL parameters, and due to this, Items with the same name cannot be queried.
The slugify module with the help of helper functions generates unique slugs for items with the same name.
For example, `bat` will be generated for `Bat`, and if the name is repeated, the slugs generated will be `bat-2`, `bat-3`...and so on.

## Setup
- Clone the repository using `git clone git@github.com:Sidsector9/FSND-Item-Catalog.git`
- cd into the directory using `cd FSND-Item-Catalog/`
- Run `vagrant up`
- Run `vagrant ssh`
- Run `cd /vagrant`
- Run `sudo pip install -r requirements.txt`
- Run `python server-catalog.py`
- Visit http://localhost:5000

## Features
- Categories are fixed. No CRUD operations (except for Read) can be performed on Categories.
- Items can be Created, Read, Updated and Deleted only by Logged-in Users.
- Users can Log in to the website using the Google Sign-In button on the top right.
- A **Home** button icon is provided for ease of navigation.
- A JSON endpoint for all data is available at http://localhost:5000/catalog.json
- A JSON endpoint for items for a specific category is available at `http://localhost:5000/<string:category_slug>/JSON`. For example: http://localhost:5000/cricket/JSON
- A JSON endpoint for a specific item is available at `http://localhost:5000/<string:category_slug>/<string:item_slug>/JSON`. For example: http://localhost:5000/cricket/ball/JSON

### Sample of a logged in Screen: 
<img width="953" alt="screenshot 2019-01-16 at 12 35 47 am" src="https://user-images.githubusercontent.com/17757960/51435907-74225000-1ca8-11e9-9f5d-17e72deffb4b.png">
