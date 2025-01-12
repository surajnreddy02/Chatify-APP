from myapp import create_app, db

# Create an app context and initialize the database
app = create_app()
with app.app_context():
    db.create_all()

print("Database initialized successfully!")
