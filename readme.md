<h1 align="center">
    Report is Ready
</h1>

## Introduction

The project consists of one or many CSV file extraction of a gmail attachment with the gmail API and to rewrite the data on a PostgreSQL database.

## What's in the box!

The single Python file responds to the following problematic:
- Etablish a connection with Gmail API
- List all Email IDs from the last month
- Find and list EmailID and attachmentID (if exists) for a given Subject
- Download a CSV attachment from a given EmailID and attachmentID
- Etablish a connection to a PostgreSQL database
- Rewrite the CSV content in the database

## Install psycopg2

Building Psycopg requires a few prerequisites (a C compiler, some development packages).
More informations can be found on https://pypi.org/project/psycopg2/

If prerequisites are met, you can install psycopg like any other Python package:
```bash
pip install psycopg2
```

You can also obtain a stand-alone package, not requiring a compiler or external libraries, by installing the psycopg2-binary package from PyPI:

```bash
pip install psycopg2-binary
```

## Ideas, futur work

### Use POSTGRES-EASYTALK

Postgres easy talk is an user-friendly query tool that provides an easier communication system in automated dabatabase interaction.

I made this query tool a few months ago in order to make differents automated queries for my personal needs on a RaspberryPi plateform.
The project is available on https://github.com/romainledru/Postgres-EasyTalk

### Improve the data Types

Data types on PostgreSQL are all set to 'TEXT'.
I decided to go with this way since there was no requirements with the database schema and for an easier implementation.
The user can take back the data and then change its type for his needs.

But maybe giving a specific type would allow that some computations could direclty be done with DB-queries (such as mean for example).

### Check for double

There is no check for double entries.
This could be a good advantage since there will be more 'report' over the time. Double entries could appear on 2 differents reports.
But, on the other hand, it would make the time of computation growing fast with the amount of reports over the time.


### Send back a confirmation email

After rewriting on the database, it could be nice to send back a confirmation email, giving some data such as:
- merging status
- time computation
- problems occured on CSV file
- status of the entire database
- next due report

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

To contribute to Report_is_ready, follow these steps:

1. Fork this repository.
2. Create a branch: `git checkout -b <branch_name>`.
3. Make your changes and commit them: `git commit -m '<commit_message>'`
4. Push to the original branch: `git push origin <project_name>/<location>`
5. Create the pull request.

Alternatively see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## Contact

If you want to contact me, you can reach me at romain.ledru2@gmail.com
