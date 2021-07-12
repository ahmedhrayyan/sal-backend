# Sal

Sal (taken from Arabic word سل which means Ask) is QA Engine based on PostgreSQL database system, Python Flask micro framework and ReactJS library.

This repo contains Sal backend only, Sal frontend repo lives [here]('fd')

### Sal live version is [here](https://sal22.herokuapp.com/).

## Motivation

The project was started as a final project for Udacity Full Stack Nanodegree program but after investing a lot of time and energy in the project to make it a complete fully functional app, I decided to make the project as a guide to create a full stack web app using python and react, though really understanding the project will help you with any other tech stack.

I will continue to maintain the project, update any unclear or sluggish code, comment here and there to make the code as readable as possible thus making it easier for beginners (and advanced) developers to understand how the app functions.

By the way, **contribution are really welcomed**

## Tech Stack

The app backend tech stack includes:

- **PostgreSQL** as our database of choice.
- **SQLAlchemy ORM** to be our ORM library of choice.
- **Python3** and **Flask** as our server language and server framework.
- **Flask-Migrate** for creating and running schema migrations.
- **AUTOPEP8** as backend style guide

## Project Structure

```
├── README.md
└── tests
├── .editorconfig
├── .gitignore
├── .env.example
├── requirements.txt
├── Procfile
├── app.py
├── config.py
├── migrations
├── templates
|   └── index.html
├── db
|   ├── models.py
|   └── __init__.py
├── auth
└── tests
```

### Highlight Folders:

- `auth` -- Contains all authentication logic
- `db` -- Contains database models and setup

### Highlight Files:

- `app.py` -- The main entry point which contains flask app (All routes are defined within it)
- `config.py` -- Contains required application config
- `Procfile` -- For <a href="https://www.heroku.com/" target="_blank">Heroku</a> deployment
- `.env.example` -- Contains required environment variables

## Issues

If you have an issue, please open it in the issues tab and I will respond ASAP.

## Documentation

Please check [wiki](https://github.com/ahmedhrayyan/sal-backend/wiki) for Details about Getting Started, Deployment and API Reference
