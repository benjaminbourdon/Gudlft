from locust import HttpUser, task


class BasicUser(HttpUser):
    # wait_time = between(1, 5)

    @task
    def index(self):
        self.client.get("/")

    @task
    def book(self):
        club = "Iron Temple"
        competition = "Fall Classic"
        url = f"/book/{competition}/{club}"
        self.client.get(url)

    @task
    def showSummary(self):
        email = "john@simplylift.co"
        self.client.post("/showSummary", data={"email": email})

    @task
    def purchasePlaces(self):
        club = "Iron Temple"
        competition = "Fall Classic"
        places = 1
        self.client.post(
            "/purchasePlaces",
            data={"competition": competition, "club": club, "places": places},
        )

    @task
    def pointsBoard(self):
        self.client.get("/pointsBoard")

    @task
    def logout(self):
        self.client.get("/logout")
