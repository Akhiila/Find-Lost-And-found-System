# FindIt — Smart Lost-and-Found Management System

## About the Project
FindIt is a web-based application that helps users report lost and found items. Users can search existing reports and view possible matches to make it easier to recover misplaced belongings.

## Features
- Report lost items
- Report found items
- Search reports by item name or location
- View recent reports
- Find possible matches based on item name and category
- Store item reports in MongoDB Atlas

## Technologies Used
- Python
- Flask
- MongoDB Atlas
- PyMongo
- HTML and CSS
- Git and GitHub

## Database
The project uses MongoDB Atlas with a database named `findit_db` and a collection named `items`.

## How to Run
1. Clone or download this repository.
2. Open the project folder in VS Code.
3. Create and activate a Python virtual environment.
4. Install dependencies:

   `pip install -r requirements.txt`

5. Create a `.env` file and configure your own MongoDB connection URI.
6. Run the application:

   `python app.py`

7. Open `http://127.0.0.1:5000` in your browser.

## Security
Keep your MongoDB connection URI and database password private. Never upload your `.env` file to GitHub.

## Future Enhancements
- User login and registration
- Item image uploads
- Improved matching using item descriptions and locations
- Notifications for possible matches
