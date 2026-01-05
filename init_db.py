from database import Base, engine
import models  # <-- PRIVALO BŪTI

def init_db():
    print("📦 Kuriamos DB lentelės...")
    print("🔍 Rastos lentelės:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    print("✅ Lentelės sukurtos")

if __name__ == "__main__":
    init_db()
