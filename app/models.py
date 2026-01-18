import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID, JSONB


class Puzzle(db.Model):
    """Crossword puzzle model."""
    
    __tablename__ = 'puzzles'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False)
    topic = db.Column(db.String(100), nullable=False, index=True)
    difficulty = db.Column(db.String(50), default='medium')
    grid_size = db.Column(db.Integer, nullable=False)
    grid_data = db.Column(JSONB, nullable=False)
    across_clues = db.Column(JSONB, nullable=False)
    down_clues = db.Column(JSONB, nullable=False)
    clue_positions = db.Column(JSONB, nullable=False)
    publish_date = db.Column(db.Date, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one puzzle per topic per day
    __table_args__ = (
        db.UniqueConstraint('topic', 'publish_date', name='uq_topic_publish_date'),
        db.Index('idx_topic_date', 'topic', 'publish_date'),
    )
    
    def __repr__(self):
        return f'<Puzzle {self.title} - {self.topic} - {self.publish_date}>'
    
    def to_dict(self):
        """Convert puzzle to dictionary for API response."""
        return {
            'id': str(self.id),
            'title': self.title,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'gridSize': self.grid_size,
            'acrossClues': self.across_clues,
            'downClues': self.down_clues,
            'answers': self.grid_data,
            'cluePositions': self.clue_positions,
            'publishDate': self.publish_date.isoformat(),
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
