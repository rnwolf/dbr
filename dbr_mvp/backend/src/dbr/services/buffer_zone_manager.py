# src/dbr/services/buffer_zone_manager.py
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session
from dbr.models.schedule import Schedule, ScheduleStatus
from dbr.models.board_config import BoardConfig


class BufferZoneStatus(Enum):
    """Buffer zone status enumeration"""
    GREEN = "green"      # Healthy - low occupancy
    YELLOW = "yellow"    # Warning - medium occupancy
    RED = "red"          # Critical - high occupancy
    CRITICAL = "critical" # Overflow - beyond capacity


@dataclass
class BufferAlert:
    """Buffer zone alert data structure"""
    zone: str
    severity: str
    message: str
    occupancy_count: int
    capacity: int
    timestamp: str


class BufferZoneManager:
    """Manager for DBR buffer zone monitoring and health metrics"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_buffer_configuration(self, board_config_id: str) -> Dict[str, Any]:
        """Get buffer zone configuration for a board"""
        
        board_config = self.session.query(BoardConfig).filter_by(id=board_config_id).first()
        if not board_config:
            raise ValueError(f"Board configuration {board_config_id} not found")
        
        pre_size = board_config.pre_constraint_buffer_size
        post_size = board_config.post_constraint_buffer_size
        
        return {
            "board_config_id": board_config_id,
            "pre_constraint_buffer_size": pre_size,
            "post_constraint_buffer_size": post_size,
            "total_board_size": pre_size + 1 + post_size,  # pre + CCR + post
            "pre_constraint_start": -pre_size,
            "pre_constraint_end": -1,
            "ccr_position": 0,
            "post_constraint_start": 1,
            "post_constraint_end": post_size,
            "time_unit": board_config.time_unit
        }
    
    def get_zone_color_thresholds(self, board_config_id: str) -> Dict[str, Dict[str, int]]:
        """Get color thresholds for buffer zones"""
        
        config = self.get_buffer_configuration(board_config_id)
        pre_size = config["pre_constraint_buffer_size"]
        post_size = config["post_constraint_buffer_size"]
        
        return {
            "pre_constraint": {
                "red_threshold": pre_size,           # 100% full
                "yellow_threshold": max(1, int(pre_size * 0.6)),  # 60% full or more
                "green_threshold": max(0, int(pre_size * 0.4))    # Less than 40%
            },
            "post_constraint": {
                "red_threshold": post_size,          # 100% full
                "yellow_threshold": max(1, int(post_size * 0.6)), # 60% full or more
                "green_threshold": max(0, int(post_size * 0.4))   # Less than 40%
            }
        }
    
    def calculate_zone_status(self, board_config_id: str) -> Dict[str, Dict[str, Any]]:
        """Calculate current status of all buffer zones"""
        
        config = self.get_buffer_configuration(board_config_id)
        thresholds = self.get_zone_color_thresholds(board_config_id)
        
        # Get all active schedules for this board
        schedules = self.session.query(Schedule).filter_by(
            board_config_id=board_config_id
        ).filter(Schedule.status != ScheduleStatus.COMPLETED).all()
        
        # Count schedules in each zone
        pre_constraint_count = 0
        post_constraint_count = 0
        ccr_occupied = False
        
        for schedule in schedules:
            pos = schedule.time_unit_position
            if pos < 0:
                pre_constraint_count += 1
            elif pos == 0:
                ccr_occupied = True
            elif pos > 0:
                post_constraint_count += 1
        
        # Calculate pre-constraint zone status
        pre_size = config["pre_constraint_buffer_size"]
        pre_percentage = (pre_constraint_count / pre_size) * 100 if pre_size > 0 else 0
        pre_status = self._determine_zone_status(pre_constraint_count, thresholds["pre_constraint"])
        
        # Calculate post-constraint zone status
        post_size = config["post_constraint_buffer_size"]
        post_percentage = (post_constraint_count / post_size) * 100 if post_size > 0 else 0
        post_status = self._determine_zone_status(post_constraint_count, thresholds["post_constraint"])
        
        return {
            "pre_constraint": {
                "status": pre_status,
                "occupancy_count": pre_constraint_count,
                "occupancy_percentage": round(pre_percentage, 2),
                "capacity": pre_size,
                "available_slots": max(0, pre_size - pre_constraint_count)
            },
            "post_constraint": {
                "status": post_status,
                "occupancy_count": post_constraint_count,
                "occupancy_percentage": round(post_percentage, 2),
                "capacity": post_size,
                "available_slots": max(0, post_size - post_constraint_count)
            },
            "ccr": {
                "occupied": ccr_occupied,
                "status": BufferZoneStatus.RED if ccr_occupied else BufferZoneStatus.GREEN
            }
        }
    
    def _determine_zone_status(self, count: int, thresholds: Dict[str, int]) -> BufferZoneStatus:
        """Determine zone status based on occupancy count and thresholds"""
        
        if count >= thresholds["red_threshold"]:
            return BufferZoneStatus.RED
        elif count >= thresholds["yellow_threshold"]:
            return BufferZoneStatus.YELLOW
        else:
            return BufferZoneStatus.GREEN
    
    def generate_buffer_alerts(self, board_config_id: str) -> List[BufferAlert]:
        """Generate alerts for buffer zone violations"""
        
        from datetime import datetime, timezone
        
        zone_status = self.calculate_zone_status(board_config_id)
        penetration = self.detect_buffer_penetration(board_config_id)
        alerts = []
        
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Check for buffer penetration (critical)
        if penetration["has_penetration"]:
            for zone in penetration["penetrated_zones"]:
                alerts.append(BufferAlert(
                    zone=zone,
                    severity="CRITICAL",
                    message=f"Buffer penetration detected in {zone} zone. Overflow count: {penetration['overflow_count']}",
                    occupancy_count=penetration["overflow_count"],
                    capacity=0,  # Beyond capacity
                    timestamp=current_time
                ))
        
        # Check pre-constraint buffer
        pre_zone = zone_status["pre_constraint"]
        if pre_zone["status"] == BufferZoneStatus.RED:
            alerts.append(BufferAlert(
                zone="pre_constraint",
                severity="RED",
                message=f"Pre-constraint buffer is full ({pre_zone['occupancy_count']}/{pre_zone['capacity']} slots occupied)",
                occupancy_count=pre_zone["occupancy_count"],
                capacity=pre_zone["capacity"],
                timestamp=current_time
            ))
        elif pre_zone["status"] == BufferZoneStatus.YELLOW:
            alerts.append(BufferAlert(
                zone="pre_constraint",
                severity="YELLOW",
                message=f"Pre-constraint buffer is {pre_zone['occupancy_percentage']}% full",
                occupancy_count=pre_zone["occupancy_count"],
                capacity=pre_zone["capacity"],
                timestamp=current_time
            ))
        
        # Check post-constraint buffer
        post_zone = zone_status["post_constraint"]
        if post_zone["status"] == BufferZoneStatus.RED:
            alerts.append(BufferAlert(
                zone="post_constraint",
                severity="RED",
                message=f"Post-constraint buffer is full ({post_zone['occupancy_count']}/{post_zone['capacity']} slots occupied)",
                occupancy_count=post_zone["occupancy_count"],
                capacity=post_zone["capacity"],
                timestamp=current_time
            ))
        elif post_zone["status"] == BufferZoneStatus.YELLOW:
            alerts.append(BufferAlert(
                zone="post_constraint",
                severity="YELLOW",
                message=f"Post-constraint buffer is {post_zone['occupancy_percentage']}% full",
                occupancy_count=post_zone["occupancy_count"],
                capacity=post_zone["capacity"],
                timestamp=current_time
            ))
        
        return alerts
    
    def get_buffer_health_metrics(self, board_config_id: str) -> Dict[str, Any]:
        """Get comprehensive buffer health metrics"""
        
        zone_status = self.calculate_zone_status(board_config_id)
        config = self.get_buffer_configuration(board_config_id)
        
        # Calculate overall status (worst of all zones)
        statuses = [
            zone_status["pre_constraint"]["status"],
            zone_status["post_constraint"]["status"]
        ]
        
        overall_status = BufferZoneStatus.GREEN
        if BufferZoneStatus.RED in statuses:
            overall_status = BufferZoneStatus.RED
        elif BufferZoneStatus.YELLOW in statuses:
            overall_status = BufferZoneStatus.YELLOW
        
        # Count total schedules
        total_schedules = (
            zone_status["pre_constraint"]["occupancy_count"] +
            zone_status["post_constraint"]["occupancy_count"] +
            (1 if zone_status["ccr"]["occupied"] else 0)
        )
        
        # Calculate flow metrics
        flow_metrics = self._calculate_flow_metrics(board_config_id, zone_status)
        
        return {
            "board_config_id": board_config_id,
            "overall_status": overall_status,
            "total_schedules": total_schedules,
            "ccr_occupied": zone_status["ccr"]["occupied"],
            "pre_constraint": zone_status["pre_constraint"],
            "post_constraint": zone_status["post_constraint"],
            "flow_metrics": flow_metrics,
            "buffer_configuration": config
        }
    
    def detect_buffer_penetration(self, board_config_id: str) -> Dict[str, Any]:
        """Detect buffer zone penetration (overflow beyond capacity)"""
        
        config = self.get_buffer_configuration(board_config_id)
        
        # Get all active schedules
        schedules = self.session.query(Schedule).filter_by(
            board_config_id=board_config_id
        ).filter(Schedule.status != ScheduleStatus.COMPLETED).all()
        
        penetrated_zones = []
        overflow_positions = []
        overflow_count = 0
        
        # Check for positions beyond buffer boundaries
        for schedule in schedules:
            pos = schedule.time_unit_position
            
            # Check pre-constraint penetration (position < -buffer_size)
            if pos < config["pre_constraint_start"]:
                if "pre_constraint" not in penetrated_zones:
                    penetrated_zones.append("pre_constraint")
                overflow_positions.append(pos)
                overflow_count += 1
            
            # Check post-constraint penetration (position > buffer_size)
            elif pos > config["post_constraint_end"]:
                if "post_constraint" not in penetrated_zones:
                    penetrated_zones.append("post_constraint")
                overflow_positions.append(pos)
                overflow_count += 1
        
        return {
            "has_penetration": len(penetrated_zones) > 0,
            "penetrated_zones": penetrated_zones,
            "overflow_count": overflow_count,
            "overflow_positions": overflow_positions
        }
    
    def _calculate_flow_metrics(self, board_config_id: str, zone_status: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate flow-related metrics for buffer health"""
        
        # Basic flow metrics calculation
        pre_occupancy = zone_status["pre_constraint"]["occupancy_percentage"]
        post_occupancy = zone_status["post_constraint"]["occupancy_percentage"]
        
        # Simple throughput rate estimation (inverse of buffer fullness)
        throughput_rate = max(0, 100 - max(pre_occupancy, post_occupancy)) / 100
        
        # Bottleneck risk (high when pre-constraint is full and post-constraint is empty)
        bottleneck_risk = "HIGH" if pre_occupancy >= 80 and post_occupancy <= 20 else "MEDIUM" if pre_occupancy >= 60 else "LOW"
        
        # Buffer penetration risk
        buffer_penetration = "HIGH" if max(pre_occupancy, post_occupancy) >= 90 else "MEDIUM" if max(pre_occupancy, post_occupancy) >= 70 else "LOW"
        
        return {
            "throughput_rate": round(throughput_rate, 2),
            "bottleneck_risk": bottleneck_risk,
            "buffer_penetration": buffer_penetration,
            "flow_balance": abs(pre_occupancy - post_occupancy)  # Difference between buffer occupancies
        }