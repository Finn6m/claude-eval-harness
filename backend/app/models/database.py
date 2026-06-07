from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

DATABASE_URL = "sqlite:///./eval.db"
# check_same_thread: False allows multiple threads to access the database
# added parameter to allow multiple threads to access the database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TestCollection(Base):
    __tablename__ = "test_collection"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    prompts = Column(JSON, nullable=False) #stores the entire prompts list as a json blob which avoids needing a seperate table for prompts
    created_at = Column(DateTime, default=datetime.utcnow)
    runs = relationship("ModelRun", back_populates="collection")

class ModelRun(Base):
    __tablename__ = "model_runs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(String, ForeignKey("test_collection.id"), nullable=False)
    model = Column(String, nullable=False)
    temperature = Column(Float, default=0.7)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    collection = relationship("TestCollection", back_populates="runs")
    results = relationship("TestResult", back_populates="run")

class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("model_runs.id"), nullable=False)
    prompt_id = Column(String, nullable=False)
    prompt_text = Column(Text, nullable=False)
    model_output = Column(Text, nullable=False)
    failure_category = Column(String, nullable=True)
    is_failure = Column(Integer, default=0)
    judge_reasoning = Column(Text, nullable=True)
    judge_confidence = Column(Float, nullable=True)
    low_confidence = Column(Integer, default=0)
    detection_method = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    run = relationship("ModelRun", back_populates="results")