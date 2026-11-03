
import os
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template_string
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, serverSelectionTimeoutMS=5000) if uri else None
db = client["findit_db"] if client else None

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FindIt | Lost & Found</title>
<style>
* { box-sizing: border-box; }
body {
  margin: 0; font-family: Arial, sans-serif;
  background: #f4f6fb; color: #17233d;
}
nav {
  background: #182747; color: white; padding: 20px 7%;
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
}
nav h2 { margin: 0; }
nav a { color: white; text-decoration: none; margin-left: 18px; }
.hero {
  padding: 55px 7%; background: linear-gradient(120deg,#e4eaff,#f8faff);
}
.hero h1 { font-size: 38px; margin-bottom: 10px; }
.hero p { color: #5b6780; line-height: 1.6; }
.container { padding: 30px 7%; }
.cards {
  display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr));
  gap: 18px; margin: 25px 0;
}
.card, form {
  background: white; padding: 22px; border-radius: 14px;
  box-shadow: 0 5px 20px #1727470d;
}
.card h3 { margin-top: 0; }
.btn {
  display: inline-block; background: #435fe5; color: white;
  padding: 12px 17px; border: 0; border-radius: 8px;
  text-decoration: none; cursor: pointer; margin: 5px 5px 5px 0;
}
.secondary { background: #13866b; }
input, select, textarea {
  width: 100%; padding: 12px; margin: 8px 0 15px;
  border: 1px solid #d5dbea; border-radius: 7px;
}
label { font-weight: bold; font-size: 14px; }
.item { border-left: 4px solid #435fe5; }
small { color: #64718a; }
footer { text-align: center; padding: 25px; color: #64718a; }
</style>
</head>
<body>
<nav>
  <h2>🔎 FindIt</h2>
  <div>
    <a href="/">Home</a>
    <a href="/report/lost">Report Lost</a>
    <a href="/report/found">Report Found</a>
    <a href="/items">Browse Items</a>
  </div>
</nav>

<section class="hero">
  <h1>Lost something? Let's find it.</h1>
  <p>A smarter way to reconnect people with their missing belongings.
     Report an item or search for something that has been found.</p>
  <a class="btn" href="/report/lost">Report Lost Item</a>
  <a class="btn secondary" href="/report/found">Report Found Item</a>
</section>

<div class="container">
  <h2>How FindIt Works</h2>
  <div class="cards">
    <div class="card"><h3>📌 Report</h3>
      <p>Submit details about a lost or found belonging.</p></div>
    <div class="card"><h3>🔍 Search</h3>
      <p>Browse records and filter by item name or location.</p></div>
    <div class="card"><h3>🤝 Reconnect</h3>
      <p>Use item details to help identify a possible match.</p></div>
  </div>

  <h2>Search Items</h2>
  <form action="/items" method="get">
    <input name="q" placeholder="Search item name or location">
    <button class="btn">Search</button>
  </form>

  <h2>Recent Reports</h2>
  <div class="cards">
  {% for item in items %}
    <div class="card item">
      <h3>{{ item.item_name }}</h3>
      <p><b>Status:</b> {{ item.report_type|title }}</p>
      <p><b>Category:</b> {{ item.category }}</p>
      <p><b>Location:</b> {{ item.location }}</p>
      <small>{{ item.date_reported }}</small>
    </div>
  {% else %}
    <div class="card">
      <p>No reports yet. Be the first to report an item!</p>
    </div>
  {% endfor %}
  </div>
</div>
<footer>FindIt — Helping lost belongings find their way home.</footer>
</body>
</html>
"""

FORM = """
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Report Item | FindIt</title>
<style>
body {font-family:Arial;background:#f4f6fb;color:#17233d;margin:0;padding:30px 6%}
form {max-width:600px;margin:30px auto;background:white;padding:28px;border-radius:14px}
input,select,textarea {width:100%;padding:12px;margin:8px 0 16px;box-sizing:border-box;border:1px solid #d5dbea;border-radius:7px}
button,a {display:inline-block;padding:12px 17px;border:0;border-radius:8px;background:#435fe5;color:white;text-decoration:none;cursor:pointer}
</style></head><body>
<a href="/">← Home</a>
<form method="post">
<h1>Report {{ kind|title }} Item</h1>
<label>Item name</label><input name="item_name" required>
<label>Category</label>
<select name="category" required>
<option value="">Choose category</option>
<option>Electronics</option><option>Books & Stationery</option>
<option>Identity Cards</option><option>Bags</option>
<option>Keys</option><option>Clothing</option><option>Other</option>
</select>
<label>Description</label><textarea name="description" rows="3" required></textarea>
<label>Location</label><input name="location" required>
<label>Date</label><input type="date" name="item_date" required>
<label>Your name</label><input name="reporter_name" required>
<label>Contact email</label><input type="email" name="contact_email" required>
<button type="submit">Submit Report</button>
</form></body></html>
"""

@app.route("/")
def home():
    items = []
    if db is not None:
        try:
            items = list(db.items.find().sort("_id", -1).limit(6))
        except Exception:
            app.logger.exception("Could not load recent reports")
    return render_template_string(HTML, items=items)


@app.route("/report/<kind>", methods=["GET", "POST"])
def report(kind):
    if kind not in ("lost", "found"):
        return "Invalid report type", 404

    if request.method == "POST":
        if db is None:
            return "MongoDB URI is missing from .env", 500

        record = {
            "report_type": kind,
            "item_name": request.form["item_name"].strip(),
            "category": request.form["category"],
            "description": request.form["description"].strip(),
            "location": request.form["location"].strip(),
            "item_date": request.form["item_date"],
            "reporter_name": request.form["reporter_name"].strip(),
            "contact_email": request.form["contact_email"].strip(),
            "date_reported": datetime.now().strftime("%d %b %Y"),
            "status": "open"
        }

        try:
            db.items.insert_one(record)

            opposite_kind = "found" if kind == "lost" else "lost"

            matches = list(db.items.find({
    "report_type": opposite_kind,
    "category": record["category"],
    "status": "open",
    "item_name": {
        "$regex": f"^{record['item_name'].strip()}$",
        "$options": "i"
    }
}))


            return render_template_string("""
                <h2>Report submitted successfully!</h2>
                <p>Item: {{ item_name }}</p>
                <h3>Possible matches</h3>
                {% if matches %}
                    {% for match in matches %}
                        <p>{{ match.item_name }} — {{ match.location }}</p>
                    {% endfor %}
                {% else %}
                    <p>No matching reports found yet.</p>
                {% endif %}
                <a href="/">Back to Home</a>
            """, item_name=record["item_name"], matches=matches)
        except Exception:
            app.logger.exception("Could not save report")
            return "Could not save the report. Check the server logs.", 500

    return render_template_string(FORM, kind=kind)


@app.route("/items")
def items():
    if db is None:
        return "MongoDB URI is missing from .env", 500

    query = request.args.get("q", "").strip()
    filters = {}

    if query:
        filters["$or"] = [
            {"item_name": {"$regex": query, "$options": "i"}},
            {"location": {"$regex": query, "$options": "i"}}
        ]

    try:
        records = list(db.items.find(filters).sort("_id", -1))
    except Exception:
        app.logger.exception("Could not load items")
        return "Could not retrieve items from MongoDB.", 500

    return render_template_string(HTML, items=records)


@app.route("/test-db")
def test_db():
    if client is None:
        return "MONGODB_URI is missing from .env", 500
    try:
        client.admin.command("ping")
        return "MongoDB Atlas connected successfully!"
    except Exception:
        app.logger.exception("MongoDB connection failed")
        return "Connection failed. Check Atlas settings.", 500


if __name__ == "__main__":
    app.run(debug=True)
