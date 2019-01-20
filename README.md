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

Run `pip install python-slugify` to install slugify.

As per the requirements, the items are queried by the URL parameters, and due to this, Items with the same name cannot be queried.
The slugify module with the help of helper functions generates unique slugs for items with the same name.
For example, `bat` will be generated for `Bat`, and if the name is repeated, the slugs generated will be `bat-2`, `bat-3`...and so on.

## Setup
- Clone the repository using ``
- cd into the directory using ``
- Run `python python server-catalog.py`

## Features
- Categories are fixed. No CRUD operations (except for Read) can be performed on Categories.
- Items can be Created, Read, Updated and Deleted only by Logged-in Users.
- Users can Log in to the website using the Google Sign-In button on the top right.
- A **Home** button icon is provided for ease of navigation.
- A JSON endpoint is available at http://localhost:5000/catalog.json

### Sample of a logged in Screen: 
<img width="953" alt="screenshot 2019-01-16 at 12 35 47 am" src="https://user-images.githubusercontent.com/17757960/51435907-74225000-1ca8-11e9-9f5d-17e72deffb4b.png">
