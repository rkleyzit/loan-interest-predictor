<h1>Predicted Reference Rate ETL</h1>

<b>Run Command:</b> docker-compose -f etl-compose.yml up -d --build 

<h3>Considerations:</h3>

1. It may be possible that other rate sources are added in the future (ie: if we want to create a composite prediction) and therefore the etl should be defined in an abstract sense with a DB schema that supports multiple sources.

2. Pensford provides data in a html table as well as an Excel spreadsheet. I opted to parse the html table because it would be faster to develop and more performant.

3. Sqlite is not a production solution. I chose to use an ORM to interact with the db because it offers the ability for seamless transition to a new RBDMS, easier unit test development in an isolated environment, and built-in data validations.

4. In addition to a prod DB, it would be nice to persist the latest data in a faster key/value store (such as Redis) for the api's performance.

5. The ETL process will need to be kicked off by some job scheduler. It should have robust logging and alerting.

6. The ETL should support multiple runs daily without breaking regardless of the state the previous run left off in (success or failure). Therefore I use batches to categorize the runs and the api will query the latest available batch.

<h1>Predicted Interest Rate API</h1>

<b>Run Command:</b> docker-compose -f api-compose.yml up -d --build 

<b>Endpoint:</b> POST http://127.0.0.1:8000/api/interest-rates/predict

<h3>Considerations:</h3>

1. Since the ETL and API run in separate containers, the Sqlite file is not shared between them. Therefore I've copied a sample database to the API image for testing. In prod, the DB should be on an independent host that is accessible by both ETL and API containers.

2. In case this API will eventually host additional endpoints, I've made it simple to register new routes (just drop them into the routes folder and they will be automatically registered)

3. Unit tests are critical for ensuring the behavior is expected when making changes so I've added a few. Ideally there is a CI/CD pipeline that will execute these tests automatically on each build. For now they can be executed manually using nosetests.

4. A prod app may also need an authorization layer.

<h3>Time Spent</h3>

* ETL: 1 hour (including DB setup)

* API: 45 min

* Unit Tests: 45 min

* Refactoring and Documenting: 45 min
