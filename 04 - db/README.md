Database examples.

-   Create a database
-   Populate it with sample data
-   Factor database access into its own model layer (per Model-View-Controller)
-   Report on the contents of the database in several ways.
-   Update the contents of a database table.
-   Add new elements to a database.
-   Use database transactions to ensure data integrity.

To Run this Application
=======================

To run this application, you will first have to set up the database.
Follow these steps:

1.  Clone or refresh the `examples-db` repository from Github.
2.  Create a database file that matches the value of the `DATABASE`
    variable near the top of the `db.py` file. Make sure to create the
    file in the *same* directory where `db.py` itself is located.
3.  From the `db` directory, run the `create-db.sql` script to create
    the database tables. You should be able to right-click on the file
    and choose `Run`.
4.  Similarly, run the `init-db.sql` script.

Now you should be able to run the application:

1.  Open the `examples-db.py` file.
2.  Right click anywhere in the `examples.py` window, and choose either
    `Run` or `Debug`.
