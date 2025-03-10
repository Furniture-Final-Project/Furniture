# furniture - the furniture store

## Root Convention

All commands are [assumed to run from the root of the project] - the directory in which _this README_ is located.

## Installation

    $ pip install -r requirements.txt

## Running pre-commit


    $ pre-commit run --all-files

## Running the Server

    $ waitress-serve --call app:create_app

## Loading Sample Data into the Database

This repository has a file `sample_data.db` which is a sqlite database with sample data.
To use this when runnin the server, copy this file to `default.db` before running the server.

On Mac:

    $ cp sample_data.db default.db
    $ waitress-serve --call app:create_app
