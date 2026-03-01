import os
import shortuuid
import random
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv
from faker import Faker

# Load environment variables from .env file
load_dotenv()

# Get Neon PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file")

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to Radios
    radios = relationship("Radio", back_populates="team", cascade="all, delete")


class Radio(Base):
    __tablename__ = "radios"

    id = Column(String(22), primary_key=True, default=lambda: shortuuid.uuid())
    serial_number = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_stolen = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)

    # Relationship back to Team
    team = relationship("Team", back_populates="radios")


def generate_database(num_teams=5, radios_per_team=50):
    print("Initializing Neon PostgreSQL Database...")
    
    # Create tables if they do not exist
    Base.metadata.create_all(bind=engine)
    print("Tables created or verified.")

    db = SessionLocal()
    fake = Faker()

    print(f"Generating {num_teams} teams with {radios_per_team} radios each...")
    
    try:
        for _ in range(num_teams):
            # 1. Create Team
            new_team = Team(
                name=f"Team {fake.company()}",
                description=fake.catch_phrase()
            )
            db.add(new_team)
            db.commit()      # Commit to get the new_team.id assigned by PostgreSQL
            db.refresh(new_team)

            # 2. Assign Radios to that Team
            radios = []
            for _ in range(radios_per_team):
                radio = Radio(
                    id=shortuuid.uuid(),
                    serial_number=fake.unique.bothify(text='RAD-####-????-####', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
                    name=fake.word().capitalize() + " Tracker",
                    is_stolen=random.random() < 0.05,  # 5% chance of being stolen
                    team_id=new_team.id
                )
                radios.append(radio)
            
            # Bulk save the radios for this team
            db.add_all(radios)
            db.commit()

        print("Successfully generated and saved fake data to Neon PostgreSQL!")
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Feel free to change these numbers
    generate_database(num_teams=20, radios_per_team=250)
