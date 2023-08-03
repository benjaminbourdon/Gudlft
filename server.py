import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for

MAX_PLACES_PER_CLUB = 12

def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()
bookedPlaces = {club["name"]: dict() for club in clubs}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form['email']
    club = next((club for club in clubs if club['email'] == email), None)
    for competition in competitions:
        competition["in_future"] = (datetime.fromisoformat(competition["date"]) >= datetime.now())
        
    if club :
        return render_template('welcome.html',club=club,competitions=competitions)
    else :
        flash(f"Sorry, that email ({email}) wasn't found.")
        index_url = url_for("index")
        return redirect(index_url,code=303)
        

@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition and (datetime.fromisoformat(foundCompetition["date"]) > datetime.now()):
        nbPlacesAlreadyBooked = bookedPlaces[foundClub["name"]].get(foundCompetition["name"]) or 0
        max_places = min(int(foundClub['points']), int(foundCompetition['numberOfPlaces']), MAX_PLACES_PER_CLUB-int(nbPlacesAlreadyBooked))
        return render_template('booking.html',club=foundClub,competition=foundCompetition, max_places=max_places)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    nbPlacesAlreadyBooked = bookedPlaces[club["name"]].setdefault(competition["name"], 0)
    placesRequired = int(request.form['places'])
    if datetime.fromisoformat(competition["date"]) < datetime.now():
        flash(f"Competition has already started.")
    elif placesRequired < 0 or placesRequired > min(int(club['points']), int(competition['numberOfPlaces']), MAX_PLACES_PER_CLUB-int(nbPlacesAlreadyBooked)):
        flash(f"Number of places required ({placesRequired}) is wrong, please try again")
    else:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
        club['points'] = int(club['points'])-placesRequired
        bookedPlaces[club["name"]][competition["name"]] = nbPlacesAlreadyBooked + placesRequired
        flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/pointsBoard')
def showPointsBoard():
    return render_template('pointsbord.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))