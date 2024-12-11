import TripAdvisor.info as info
from flask import render_template, request, redirect, url_for, flash, jsonify
from TripAdvisor.models import User, Event, Category
from TripAdvisor import bcrypt, db, app
from TripAdvisor.forms import LoginForm, AddEventForm, AddUserForm
from flask_login import login_user, current_user, logout_user, login_required
import pytz
from datetime import datetime, timedelta
from math import ceil

import os

from dotenv import find_dotenv, load_dotenv

path = find_dotenv()

load_dotenv(path)

google_key = os.getenv("GOOGLE_API")


event_cache = {'events': None, 'last_updated': None}
def cacheEvents():
        est = pytz.timezone('America/New_York')
        global event_cache
        dbevents = Event.query.all()
        listevents = [{
                    'id': event.id,
                    'Name': event.name,
                    'Start': event.start.replace(tzinfo=pytz.utc).astimezone(est).strftime('%B %d %Y %I:%M%p'),
                    'End': event.end.replace(tzinfo=pytz.utc).astimezone(est).strftime('%B %d %Y %I:%M%p'),
                    'Location': event.location,
                    'Description': event.description,
                    'Categories': event.categories,
                    'Gobbler': False
        } for event in dbevents]

        events = info.getEvent() + listevents
        sortedList = sorted(events,
                        key=lambda x: datetime.strptime(x['Start'], '%B %d %Y %I:%M%p'))
        event_cache['events'] = sortedList
        event_cache['last_updated'] = datetime.now()

def getEvents():
    if event_cache['last_updated'] is None or datetime.now() - event_cache['last_updated'] > timedelta(minutes=5):
        event_cache['events'] = None

    if event_cache['events'] is None:
        cacheEvents()
    
    return event_cache['events']

restaurant_cache = {'restaurants': None, 'last_updated': None}
def cacheRestaurants():
    restaurant_cache['restaurants'] = info.getRestaurants()
    restaurant_cache['last_updated'] = datetime.now()

def getRestaurants():
    if restaurant_cache['last_updated'] is None or datetime.now() - restaurant_cache['last_updated'] > timedelta(minutes=1440):
        restaurant_cache['restaurants'] = None
    
    if restaurant_cache['restaurants'] is None:
        cacheRestaurants()
    
    return restaurant_cache['restaurants']

def toutc(local_start, local_end):
    localtz = pytz.timezone('America/New_York')
    lStart = localtz.localize(local_start)
    lEnd = localtz.localize(local_end)

    utc_start = lStart.astimezone(pytz.utc)
    utc_end = lEnd.astimezone(pytz.utc)

    return (utc_start, utc_end)

@app.route("/")
def index():

    events = getEvents()
    restaurants = getRestaurants()
    # Sort events by date and select the first 3 upcoming events
    upcoming_events = sorted(events, key=lambda x: datetime.strptime(x['Start'], '%B %d %Y %I:%M%p'))[:3]
    return render_template('home.html', title="Blacksburg Trip Advisor", events=upcoming_events, restaurants=restaurants[:3], google_key = google_key)

@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    event_type = request.args.get('event_type', 'All')

    # Parse the date strings to datetime objects if they are provided
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') if end_date_str else None
    except ValueError as e:
        flash(f"Invalid date format: {e}", 'danger')
        start_date, end_date = None, None

    # if event_cache['last_updated'] is None or datetime.now() - event_cache['last_updated'] > timedelta(minutes=5):
    #     event_cache['events'] = None

    # if event_cache['events'] is None:
    #     cacheEvents()

    events = getEvents()


    restaurants = getRestaurants()  # TripAdvisor restaurants

    # Filter events and restaurants based on the search query
    filtered_events = []
    filtered_restaurants = []


    if query:
        query = query.lower()
        filtered_events = [ev for ev in events if query in ev['Name'].lower() or query in ev['Description'].lower()]
        filtered_restaurants = [res for res in restaurants if query in res['Name'].lower() or query in res['Address'].lower()]
    else:
        filtered_events = events
        filtered_restaurants = restaurants

    # Further filter events by the date range if provided
    if start_date or end_date:
        filtered_events = [
            ev for ev in filtered_events
            if (not start_date or datetime.strptime(ev['Start'], '%B %d %Y %I:%M%p') >= start_date) and
               (not end_date or datetime.strptime(ev['Start'], '%B %d %Y %I:%M%p') <= end_date)
        ]

    # Filter events based on the event type (Online/In-Person)
    if event_type != "All":
        filtered_events = [
            ev for ev in filtered_events
            if (event_type == "Online" and ev['Location'].lower() == "online") or
               (event_type == "In-Person" and ev['Location'].lower() != "online")
        ]

    per_page = 10 
    page = int(request.args.get('page', 1)) 
    total_pages = ceil(len(filtered_events) / per_page)  

    # Paginate the events
    start = (page - 1) * per_page
    end = start + per_page
    paginated_events = events[start:end]
    # Render the search page with both filtered results
    return render_template('search.html', events=filtered_events, restaurants=filtered_restaurants, title='Search Results', google_key = google_key)



@app.route("/events", methods=['GET'])
def events():

    events = getEvents()
    per_page = 10 
    page = int(request.args.get('page', 1)) 
    total_pages = ceil(len(events) / per_page)  

    # Paginate the events
    start = (page - 1) * per_page
    end = start + per_page
    paginated_events = events[start:end]

    return render_template('events.html', events=paginated_events, title='Events', page = page, total_pages = total_pages)

@app.route("/event/<location_id>")
def event_detail(location_id):
    events = info.getEvent()
    event_details = next((ev for ev in events if ev['location_id'] == location_id), None)
    if event_details:
        return render_template('event_detail.html', event=event_details)
    else:
        return "Event not found", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=False)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Check Username and password', 'danger')
            # return redirect(url_for('l'))

    return render_template('login.html', title="Login", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/addevent', methods=['GET', 'POST'])
@login_required
def addEvent():
    form = AddEventForm()
    if form.validate_on_submit():
        utc_start, utc_end = toutc(form.start.data, form.end.data)
        event = Event(
            name=form.name.data,
            start=utc_start,
            end=utc_end,
            location=form.location.data,
            description=form.description.data,
        )
        # selected_category_ids = form.categories.data  # This is a list of IDs

        # # Fetch corresponding Category objects and associate them with the event
        # categories = Category.query.filter(Category.id.in_(selected_category_ids)).all()
        # event.categories.extend(categories)  # Add categories to the event

        db.session.add(event)
        db.session.commit()
        return redirect(url_for('events'))

    return render_template('addevent.html', title="Add Event", form=form)

@app.route("/events/<int:event_id>/edit", methods=['GET', 'POST'])
@login_required
def editEvent(event_id):
    event = Event.query.get_or_404(event_id)
    form = AddEventForm(obj=event)

    if form.validate_on_submit():
        utc_start, utc_end = toutc(form.start.data, form.end.data)
        event.name = form.name.data
        event.start = utc_start
        event.end = utc_end
        event.location = form.location.data
        event.description = form.description.data

        db.session.commit()

        return redirect(url_for("events"))

    return render_template('addevent.html', title="Edit Event", form=form, edit=True)

@app.route("/events/<int:event_id>/delete", methods=['GET', 'POST'])
@login_required
def deleteEvent(event_id):
    event = Event.query.get_or_404(event_id)

    try:
        db.session.delete(event)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting this event: {e}", "danger")

    return redirect(url_for("events"))

@app.route('/adduser', methods=['GET', 'POST'])
@login_required
def addUser():
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        )

        db.session.add(user)
        db.session.commit()
        flash('User has been added successfully', 'success')
        return redirect(url_for('addUser'))

    return render_template('adduser.html', title='Add User', form=form)
