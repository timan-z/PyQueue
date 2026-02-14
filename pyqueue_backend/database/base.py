
from sqlalchemy.orm import declarative_base # Defines the base class for all ORM models.

Base = declarative_base()   # This will be how SQLAlchemy knows what tables exist, what metadata exists, and what needs to be created.