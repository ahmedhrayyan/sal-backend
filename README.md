# Sal
Sal (taken from Arabic word سل which means Ask) is QA Engine based on PostgreSQL database system, Python Flask micro framework and ReactJS library.

Sal live version is [here](https://sal22.herokuapp.com/).

## Motivation
The project was started as a final project for Udacity Full Stack Nanodegree program but after investing a lot of time and energy in the project to make it a complete fully function app, I decided to make the project as a guide to create a full stack web app using python and react, though really understanding the project will help you with any other tech stack.

I will continue to maintain the project, update any unclear or sluggish code, comment here and there to make the code as readable as possible thus making it easier for beginners (and advanced) developers to understand how the app functions.

Please forgive me for any un clarity or bugs in the code as I designed and developed the whole project in a moth (I don’t really have a lot of time currently) so if you see something unclear, do not respect the project style guide or will make the project better do not hesitate to send a pull request or even open a new issue and I will respond to it ASAP.

By the way, CONTRIBUTIONS ARE REALLY WELCOMED

## Screenshot
image

## Tech Stack
The app tech stack includes:

* **Auth0** to be our authentication and authorization management platform.
* **PostgreSQL** as our database of choice.
* **SQLAlchemy ORM** to be our ORM library of choice.
* **Python3** and **Flask** as our server language and server framework.
* **Flask-Migrate** for creating and running schema migrations.
* **Redux** as our frontend container for the app state.
* **ReactJS**, **React Router** and **React Redux** as our frontend Framework (yes, I think all of these three libraries combined to be forming kind of a framework).
* **HTML**, **SCSS**, and **bootstrap 4**
* **Prettier** and **AUTOPEP8** as frontend and backend style guide

I have also used **Figma** (it was the first time I do but I’m really surprised how really powerful it is) and **Microsoft fluent design language** for the web to design Sal

## Project Structure
  ```sh
  ├── README.md
  ├── .editorconfig
  ├── .gitignore
  ├── migrations *** database migrations
  ├── frontend
  |   ├── README.md
  |   ├── .gitignore
  |   ├── tsconfig.json
  |   ├── package.json
  |   ├── package-lock.json
  |   ├── public
  |   └── src
  └── backend
      ├── .gitignore
      ├── requirements.txt
      ├── app
      ├── auth
      ├── database
      └── test
  ```

### Highlight Folders:
* `public` -- contains base html file which react uses when building
* `src` -- contains almost all client side code and it follows [ducks](https://www.freecodecamp.org/news/scaling-your-redux-app-with-ducks-6115955638be/) file structure
* `auth` -- contains all auth0 logic
* `database` -- contains database models and setup
* `app` -- The most important folder which contains flask app (all routes and http serving logic defined within it)

## Documentation
Please check [wiki](https://github.com/ahmedhrayyan/sal/wiki) for Details about Getting Started, Deployment and API Reference
