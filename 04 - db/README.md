# Database Examples

- Create a database
- Populate it with sample data
- Factor database access into its own model layer (per Model-View-Controller)
- Report on the contents of the database in several ways
- Update the contents of a database table
- Add new elements to a database
- Use database transactions to ensure data integrity

# To Run this Application

To run this application, you will first have to set up the database.
Follow these steps:

1. Clone or refresh the repository from Github
1. Establish a connection to PostgreSQL 
   by setting the `data_source_name` in `db.py`
1. From the `sql` directory, run the `create-db.sql` script to create
   the database tables. You should be able to right-click on the file
   and choose **Run**.
1. Similarly, run the `init-db.sql` script.

Now you should be able to run the application:

1. Right click on the `application.py` file
1. Choose **Run** or **Debug** from the pop-up menu
