# src/dbr/models/board_config.py
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from dbr.models.base import BaseModel


class BoardConfig(BaseModel):
    """Board configuration model for DBR boards"""
    __tablename__ = "board_configs"
    
    # Basic board information
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    
    # CCR configuration
    ccr_id = Column(String(36), ForeignKey('ccrs.id'), nullable=False)
    
    # Buffer configuration
    pre_constraint_buffer_size = Column(Integer, nullable=False, default=5)
    post_constraint_buffer_size = Column(Integer, nullable=False, default=3)
    
    # Time configuration
    time_unit = Column(String(20), nullable=False, default="week")
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships (can be added later when needed)
    # organization = relationship("Organization", back_populates="board_configs")
    # ccr = relationship("CCR", back_populates="board_configs")
    # schedules = relationship("Schedule", back_populates="board_config")
    
    def get_total_board_size(self) -> int:
        """Get total board size (pre + constraint + post)"""
        return self.pre_constraint_buffer_size + 1 + self.post_constraint_buffer_size
    
    def get_ccr_position(self) -> int:
        """Get the position of the CCR on the board (0-based)"""
        return self.pre_constraint_buffer_size
    
    def get_position_zone(self, position: int) -> str:
        """Get the zone name for a given position"""
        # Position 0 is the CCR, negative positions are pre-constraint, positive are post-constraint
        if position < 0:
            return "pre_constraint"
        elif position == 0:
            return "constraint"
        else:
            return "post_constraint"
    
    def is_position_valid(self, position: int) -> bool:
        """Check if a position is valid on this board"""
        return -self.pre_constraint_buffer_size <= position <= self.post_constraint_buffer_size
    
    def __repr__(self):
        return f"<BoardConfig(id={self.id}, name='{self.name}', ccr_id={self.ccr_id})>"