from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    flash,
    make_response,
    redirect
)

from slugify import slugify
from oauth2client.client import (
    flow_from_clientsecrets,
    FlowExchangeError

)
from db_functions import *
import httplib2
import json
import requests
import logging


app = Flask(__name__)
CLIENT_ID = json.loads(open('credentials.json', 'r').read())[
    'web']['client_id']


@app.route('/')
def render_main_page():
    """The route for the root page."""
    return render_template(
        'home.html',
        catalog_items=session.query(Category),
        latest_items=get_latest_items(),
        STATE=get_state(),
        login_session=login_session
    )


@app.route('/<string:category_slug>/items')
def display_category_items(category_slug):
    """The route for displaying items in each category."""
    return render_template(
        'category_items.html',
        catalog_items=session.query(Category),
        items=get_items_by_category_slug(category_slug),
        category_slug=category_slug,
        login_session=login_session,
        category=get_category_name_by_category_slug(category_slug).first()
    )


@app.route('/<string:category_slug>/<string:item_slug>')
def display_item_description(category_slug, item_slug):
    """The route for displaying iten description."""
    user_email = session.query(
        Items.user_email).filter_by(
        slug=item_slug).first()[0],
    return render_template(
        'description.html',
        STATE=get_state(),
        item_slug=item_slug,
        description=get_item_description(item_slug),
        login_session=login_session,
        user_email=user_email,
        item=get_item_by_slug(item_slug)
    )


@app.route('/item/new', methods=['GET', 'POST'])
def add_item():
    """The route for adding a new item in a category.
    Only accessible when logged in."""
    updated_slug = ''

    # If a new item is added, then add it to the
    # Items relation.
    if request.method == 'POST':
        data = request.form
        check_slug = session.query(Items).filter(
            Items.slug.like(slugify(data['title']) + "%"))

        # If slug already exists, then append increment
        # the number and append it to the item slug.
        if check_slug.count() > 0:
            updated_slug = slugify(data['title']) + \
                '-' + str((check_slug.count() + 1))
        else:
            updated_slug = slugify(data['title'])

        # Create a new item object.
        new_item = Items(
            name=data['title'],
            category_id=data['category'],
            slug=updated_slug,
            description=data['description'],
            user_email=login_session['email'])

        # Add and commit to the Items relation.
        session.add(new_item)
        session.commit()
        return render_template('item_add_success.html')

    # Show the Add Item form to add a new item.
    return render_template(
        'add_item.html',
        categories=get_categories(),
        login_session=login_session
    )


@app.route('/catalog/<string:item_slug>/edit', methods=['GET', 'POST'])
def edit_item(item_slug):
    """The route for editing an exisiting item.
    Only accessible when logged in."""

    authorized=False

    if login_session['email'] != get_item_author(item_slug):
        return render_template(
            'edit_item.html',
            authorized=authorized
        )

    # If it's an edit submission, then update the data in the
    # Items relation.
    if request.method == 'POST':
        data = request.form
        session.query(Items).filter_by(slug=data['item_slug']).update({
            'category_id': data['category'],
            'name': data['title'],
            'description': data['description']
        })
        session.commit()
        return render_template('item_updated_success.html')

    # Else show the edit form.
    authorized=True
    return render_template(
        'edit_item.html',
        categories=get_categories(),
        item=get_item_by_slug(item_slug),
        item_slug=item_slug,
        login_session=login_session,
    )


@app.route('/catalog/<string:item_slug>/delete', methods=['GET', 'POST'])
def delete_item(item_slug):
    """Asks for user confirmation before deleting an item"""

    authorized=False

    if login_session['email'] != get_item_author(item_slug):
        return render_template(
            'delete_confirmation.html',
            authorized=authorized
        )

    # If it's a delete submission, then delete it from the
    # Items relation.
    if request.method == 'POST':
        item_to_delete = session.query(Items).filter_by(slug=item_slug).one()
        session.delete(item_to_delete)
        session.commit()
        return render_template('item_deleted_success.html')

    # Else ask for 'delete confirmation' wheh the endpoint
    # is visited.
    authorized=True
    return render_template(
        'delete_confirmation.html',
        item_slug=item_slug,
        item=get_item_by_slug(item_slug),
        login_session=login_session,
        authorized=authorized
    )


@app.route('/catalog.json')
def catalog_json():
    """JSON endpoint which returns items per category."""

    # Join the Items and the Category relations.
    join_result = session.query(
        Category.id,
        Category.name,
        Items.id,
        Items.category_id,
        Items.name,
        Items.description).filter_by(
        id=Items.category_id)

    # Get all categories with its `id` and `names`.
    categories = session.query(Category.id, Category.name).all()
    item_data = {}
    category_data = []

    # Populate the `item_data` dictionary
    for result in join_result:
        if result[1] not in item_data:
            item_data[result[1]] = [{
                'cat_id': result[3],
                'description': result[5],
                'id': result[2],
                'title': result[4]
            }]
        else:
            item_data[result[1]].append({
                'cat_id': result[3],
                'description': result[5],
                'id': result[2],
                'title': result[4]
            })

    # Add items in their respective categories.
    for category in categories:
        category_data.append({
            'id': category.id,
            'name': category.name,
            'items': item_data[category.name]
        })

    # Return the data in a JSON format.
    return jsonify(Category=category_data)


@app.route('/<string:category_slug>/JSON')
def items_per_category_json(category_slug):
    """JSON endpoint which returns items of a specific category."""

    # Join the Items and the Category relations.
    join_result = session.query(
        Category.id,
        Category.name,
        Items.id,
        Items.category_id,
        Items.name,
        Items.description,
        Category.slug).filter_by(
        id=Items.category_id)

    # Get all categories with its `id` and `names`.
    categories = session.query(Category.id, Category.name, Category.slug).all()
    item_data = {}
    category_data = []

    # Populate the `item_data` dictionary
    for result in join_result:
        if result[6] == category_slug:
            if result[1] not in item_data:
                item_data[result[1]] = [{
                    'description': result[5],
                    'item_id': result[2],
                    'title': result[4]
                }]
            else:
                item_data[result[1]].append({
                    'description': result[5],
                    'item_id': result[2],
                    'title': result[4]
                })

    # Add items in their respective category.
    for category in categories:
        if category.slug == category_slug:
            category_data.append({
                'cat_id': category.id,
                'name': category.name,
                'items': item_data[category.name]
            })

    # Return the data in a JSON format.
    return jsonify(Items=category_data)


@app.route('/<string:category_slug>/<string:item_slug>/JSON')
def items_json(category_slug, item_slug):
    """JSON endpoint which returns details of a specific item."""

    # Join the Items and the Category relations.
    join_result = session.query(
        Category.id,
        Category.name,
        Items.id,
        Items.category_id,
        Items.name,
        Items.description,
        Category.slug,
        Items.slug,
        Items.user_email).filter(
        Category.id == Items.category_id,
        Items.slug == item_slug,
        Category.slug == category_slug)

    item_data = []

    for item in join_result:
        item_data.append({
            'item_id': item[2],
            'item_name': item[4],
            'item_description': item[5],
            'category_id': item[0],
            'category_name': item[1],
            'user_email': item[8]
        })

    return jsonify(Item=item_data)


@app.route('/gconnect', methods=['GET', 'POST'])
def gconnect():

    # If state doesn't match correctly, then throw 401 Unauthorized Access
    # error.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # If state matches correctly, then obtain authorization code.
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('credentials.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
        access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        logging.warning("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Confirm if the user is already connected or not.
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    return ''


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = (
        'https://accounts.google.com/o/oauth2/revoke?token=%s' %
        login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
