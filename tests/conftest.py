import pytest
import datetime

import server
from server import app as flask_app


@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True,
    })    
    yield flask_app
    
@pytest.fixture(autouse=True)
def clubs_test(monkeypatch):
    mock_clubs = [
                    # Entrées fonctionnelles
                    {
                        "name":"Club Argenté",
                        "email":"argent@club.fr",
                        "points":"25"
                    },
                    {
                        "name":"Beauclub",
                        "email":"contact@bella.com",
                        "points":"13"                    
                    },
                    {
                        "name":"The Club",
                        "email":"the-club@tmail.net",
                        "points":"11"                    
                    },
                    {
                        "name":"Delta Club",
                        "email":"delta.club@fournisseur.be",
                        "points":"1"                    
                    },
                    # Entrées problématiques
                    {
                        "name":"Club Zoologique",
                        "email":"generic@commun.com",
                        "points":"-1"
                    },
                    {
                        "name":"Yellow fanclub",
                        "email":"generic@commun.com",
                        "points":"5"                    
                    },
                ]
    monkeypatch.setattr(server, 'clubs', mock_clubs)
    
    mock_bookedPlaces = {club["name"]: dict() for club in mock_clubs}
    monkeypatch.setattr(server, 'bookedPlaces', mock_bookedPlaces)

    
@pytest.fixture(autouse=True)
def competitions_test(monkeypatch):
    mock_competitions = [
                    {
                        "name": "Janvier Festival",
                        "date": "2024-01-27 10:00:00",
                        "numberOfPlaces": "15"
                    },
                    {
                        "name": "Fevrier Classic",
                        "date": "2025-02-20 13:30:00",
                        "numberOfPlaces": "5"
                    },
                    {
                        "name": "Fall March",
                        "date": "2024-03-22 11:30:00",
                        "numberOfPlaces": "2"
                    },
                    {
                        "name": "Avril dans la rue",
                        "date": "2026-04-01 00:30:00",
                        "numberOfPlaces": "0"
                    },
                    {
                        "name": "Mai Big Camp",
                        "date": "2024-05-17 13:20:00",
                        "numberOfPlaces": "8"
                    },
                    # Compétition passée
                    {
                        "name": "June not Rune",
                        "date": "2019-06-08 20:05:00",
                        "numberOfPlaces": "13"
                    }
                ]
    monkeypatch.setattr(server, 'competitions', mock_competitions)
    
# @pytest.fixture(autouse=True)
# def now_mock(monkeypatch):
    
#     class datetime_set_now(datetime.datetime):
        
#         @classmethod
#         def now(cls):
#             return datetime.datetime.fromisocalendar(2023,1,3)

#     monkeypatch.setattr(datetime, 'datetime', datetime_set_now)