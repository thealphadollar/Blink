# Blink

For research and study on the topic of "Understanding Perceptions of Email Tracking Services for Senders and Receivers", *Blink* collects all the required email data from 
paticipants maintaining their privacy and anonymity. The data collected is only numerical and a hashed identifier (MD5 hash of participant's email address) is used to link the 
data with participant's survey response.

## To Use

The client uses pipenv and google-api-python-client for it's working.

### First Run

Below are the steps on how to use it **for the first time**:

- `pip install pipenv`
- go to project directory and run `pipenv shell --three`
- install all dependencies
    `pipenv install`
- run the project and follow the CLI
    `python3 blink/api.py`

NOTE: The browser authentication is required only once, after that the secrets
are stored and used \[forever\].

### Consecutive Run

Below are the steps that need to be followed if you've already ran the program once.
- `cd /to/project/directory`
- `pipenv shell`
- `python3 blink/api.py`

The virtual environment created in first step is used here :)

## Reset Account

To attach a new account and remove the authentication for the previous one, please delete the credentials file using
the following command.

```
rm ~/.blinkcreds
```

## Contributing

Please read CONTRIBUTING.md guide to know more.
