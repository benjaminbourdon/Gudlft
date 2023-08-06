import html

import pytest
from flask import url_for
from freezegun import freeze_time

DATE_NOW_TESTED = "2023-01-13"


def test_index(client):
    url = url_for("index")
    response = client.get(url)

    assert response.status_code == 200
    assert (
        "<h1>Welcome to the GUDLFT Registration Portal!</h1>" in response.data.decode()
    )


@pytest.mark.parametrize("secretary_mail", ["argent@club.fr", "contact@bella.com"])
def test_showSummary_success(client, secretary_mail):
    url = url_for("showSummary")
    data = {"email": secretary_mail}
    response = client.post(url, data=data)

    assert response.status_code == 200


@pytest.mark.parametrize("secretary_mail", ["unknown@mail.co", ""])
def test_showSummary_mail_unknown(client, secretary_mail):
    url = url_for("showSummary")
    data = {"email": secretary_mail}

    response = client.post(url, data=data, follow_redirects=True)
    flash_expected = f"Sorry, that email ({secretary_mail}) wasn't found."
    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.request.path == url_for("index")
    assert flash_expected in html.unescape(response.data.decode())


def test_showSummary_forbidden_get_method(client):
    url = url_for("showSummary")
    response = client.get(url)
    assert response.status_code == 405


@pytest.mark.parametrize(
    "club_tested, competition_tested, nb_places, max_bookable",
    [
        ("Club Argenté", "Janvier Festival", 15, 12),
        ("The Club", "Fevrier Classic", 5, 5),
        ("Delta Club", "Janvier Festival", 15, 1),
    ],
)
@freeze_time(DATE_NOW_TESTED)
def test_book_success(client, club_tested, competition_tested, nb_places, max_bookable):
    url = url_for(
        "book",
        competition=competition_tested,
        club=club_tested,
    )
    response = client.get(url)
    assert response.status_code == 200

    html_response = html.unescape(response.data.decode())
    expected_balises = [
        f"<h2>{competition_tested}</h2>",
        f"Places available: {nb_places}",
        f'<form action="{url_for("purchasePlaces")}" method="post">',
        f'<input type="hidden" name="club" value="{club_tested}">',
        f'<input type="hidden" name="competition" value="{competition_tested}">',
        f'<label for="places">How many places?</label><input type="number" name="places" id="" min="0" max="{max_bookable}"/>',
    ]
    for balise in expected_balises:
        assert balise in html_response


@pytest.mark.parametrize(
    "club_tested, competition_tested",
    [
        ("Beauclub", "Unknown Competition"),
        ("Unknown Club", "Fevrier Classic"),
    ],
)
@freeze_time(DATE_NOW_TESTED)
def test_book_incorrect_url(client, club_tested, competition_tested):
    url = url_for("book", competition=competition_tested, club=club_tested)
    with pytest.raises(IndexError):
        response = client.get(url)


@pytest.mark.parametrize(
    "club_tested, competition_tested",
    [
        ("Club Argenté", "June not Rune"),
    ],
)
@freeze_time(DATE_NOW_TESTED)
def test_book_past_competition(client, club_tested, competition_tested):
    url = url_for("book", competition=competition_tested, club=club_tested)
    response = client.get(url)
    expected_flash = "Something went wrong-please try again"

    assert response.status_code == 200
    assert expected_flash in html.unescape(response.data.decode())


@pytest.mark.parametrize(
    "club_tested, competition_tested, booked_places, remaining_points",
    [
        ("Club Argenté", "Janvier Festival", 5, 20),
        ("The Club", "Fevrier Classic", 5, 6),
        ("Delta Club", "Janvier Festival", 0, 1),
    ],
)
@freeze_time(DATE_NOW_TESTED)
def test_purchasePlaces_success(
    client, club_tested, competition_tested, booked_places, remaining_points
):
    url = url_for("purchasePlaces")
    data = {
        "competition": competition_tested,
        "club": club_tested,
        "places": booked_places,
    }
    response = client.post(url, data=data)
    html_response = html.unescape(response.data.decode())
    expected_flash = "Great-booking complete!"

    assert response.status_code == 200
    assert expected_flash in html_response
    assert f" Points available: {remaining_points}" in html_response

    from server import bookedPlaces

    assert bookedPlaces[club_tested][competition_tested] == booked_places


@freeze_time(DATE_NOW_TESTED)
def test_purchasePlaces_started_competition(client):
    url = url_for("purchasePlaces")

    club_tested = "Delta Club"
    competition_tested = "June not Rune"
    data = {
        "competition": competition_tested,
        "club": club_tested,
        "places": 1,
    }
    response = client.post(url, data=data)
    expected_flash = "Competition has already started."

    assert response.status_code == 200
    assert expected_flash in html.unescape(response.data.decode())


@pytest.mark.parametrize(
    "club_tested, competition_tested, places_required",
    [
        ("The Club", "Fall March", 3),  # Not enough places
        ("Delta Club", "Janvier Festival", 2),  # Not enough club points
        ("Beauclub", "Janvier Festival", 13),  # More than absolute max of 12
    ],
)
@freeze_time(DATE_NOW_TESTED)
def test_purchasePlaces_invalid_booking(
    client, club_tested, competition_tested, places_required
):
    url = url_for("purchasePlaces")
    data = {
        "competition": competition_tested,
        "club": club_tested,
        "places": places_required,
    }
    response = client.post(url, data=data)
    html_response = html.unescape(response.data.decode())
    expected_msg = (
        f"Number of places required ({places_required}) is wrong, please try again"
    )

    assert response.status_code == 200
    assert expected_msg in html_response


def test_purchasePlaces_forbidden_get_method(client):
    url = url_for("purchasePlaces")
    response = client.get(url)
    assert response.status_code == 405


def test_pointsBoard_success(client):
    url = url_for("showPointsBoard")
    response = client.get(url)

    assert response.status_code == 200


def test_logout_success(client):
    url = url_for("logout")
    response = client.get(url, follow_redirects=True)

    assert response == 200
    assert len(response.history) == 1
