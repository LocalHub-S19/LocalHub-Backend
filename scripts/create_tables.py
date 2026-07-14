from app.db import engine, Base
import app.models  # ensure models are imported so metadata populated

Base.metadata.create_all(bind=engine)
print("tables created")