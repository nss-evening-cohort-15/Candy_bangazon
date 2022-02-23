# Bangazon Platform API

Bangazon is an api for users to buy and sell products

## Local Setup

1. Clone this repository and change to the directory in the terminal.
1. Run `pipenv shell`
1. Run `pipenv install`
1. Seed database: `./seed_data.sh` This will migrate and run a `seed_db` command. Take look at the `seed_data.sh` to see what it runs. Then open `bangazon_api/management/commands/seed_db.py` file to see what the `seed_db` does

Now that your database is set up all you have to do is run the command:

```sh
python manage.py runserver
```

## Bangazon ERD

Here is the ERD for the models in the api: https://drawsql.app/nss-2/diagrams/bangazon/embed

## Documentation

To make it easier for onboarding new developers, there is a documentation site made with Swagger that allows the developer to make requests and view the response
1. Run the server
1. Go to http://localhost:8000/swagger
2. Find and open the register docs and click `Try it out`
3. Fill out the json and press `Execute`
4. Copy the token that is returned
5. Scroll back to the top of the page
6. Click on `Authorize`
7. In the value input add `Token <the new token>`, then click authorize
8. Try to get a list of categories in the browser
9. If this doesn't work, reach out to your senior

Once you're logged into the swagger docs, try out a few other requests so you can see what each endpoint does. There is information in the docs about what status and data will be returned with each response. If you want to switch users, look in the `auth_token` table to grab a different token.
