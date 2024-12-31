from app import app, db  

print("Initializing the database...")

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
