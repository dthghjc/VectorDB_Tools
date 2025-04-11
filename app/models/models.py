import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, UniqueConstraint
from sqlalchemy.sql import func

from .database import Base

class SchemaModel(Base):
    __tablename__ = "schemas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(String(1024), nullable=True)
    # Store fields as a JSON list of dictionaries, e.g.,
    # [{'name': 'field1', 'type': 'str', 'is_primary': False, 'is_vector': False, 'dim': None},
    #  {'name': 'vector_field', 'type': 'vector<float>', 'is_primary': False, 'is_vector': True, 'dim': 1536}]
    fields = Column(JSON, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Ensure schema names are unique
    __table_args__ = (UniqueConstraint('name', name='uq_schema_name'),)

    def __repr__(self):
        return f"<SchemaModel(id={self.id}, name='{self.name}')>"

class UploadLog(Base):
    __tablename__ = "upload_logs"

    id = Column(Integer, primary_key=True, index=True)
    schema_name = Column(String(255), index=True, nullable=False)
    original_filename = Column(String(512), nullable=True)
    processed_filename = Column(String(512), nullable=True) # e.g., JSONL after processing
    vectorized_filename = Column(String(512), nullable=True) # e.g., JSONL after vectorization
    uploaded_filename = Column(String(512), nullable=False) # The final file uploaded to Milvus
    record_count = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default='Success') # e.g., Success, Failed
    message = Column(String(1024), nullable=True) # Optional error message
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UploadLog(id={self.id}, schema='{self.schema_name}', file='{self.uploaded_filename}', status='{self.status}')>" 