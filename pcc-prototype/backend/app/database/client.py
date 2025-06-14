import duckdb
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseClient:
    def __init__(self, db_path: str = "/app/data/pcc.db"):
        self.db_path = db_path
        self.conn = None
        
    async def init_database(self):
        """Initialize database schema"""
        self.conn = duckdb.connect(self.db_path)
        
        # Create tables
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS hl7_events (
                id VARCHAR PRIMARY KEY,
                event_type VARCHAR,
                patient_id VARCHAR,
                bed_id VARCHAR,
                timestamp TIMESTAMP,
                data JSON
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS beds (
                bed_id VARCHAR PRIMARY KEY,
                unit VARCHAR,
                status VARCHAR,
                patient_id VARCHAR,
                admission_time TIMESTAMP,
                expected_discharge TIMESTAMP,
                discharge_barriers JSON
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id VARCHAR PRIMARY KEY,
                name VARCHAR,
                age INTEGER,
                diagnosis VARCHAR,
                admission_time TIMESTAMP,
                discharge_status VARCHAR,
                barriers JSON,
                metadata JSON
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id VARCHAR PRIMARY KEY,
                type VARCHAR,
                severity VARCHAR,
                message VARCHAR,
                data JSON,
                timestamp TIMESTAMP
            )
        """)
        
        # Initialize 200 beds
        await self._initialize_beds()
        
    async def _initialize_beds(self):
        """Initialize hospital beds"""
        units = ['ICU', 'MICU', 'SICU', 'TELE', 'MED-SURG', 'ORTHO', 'NEURO', 'CARDIAC']
        beds_per_unit = 25
        
        for unit_idx, unit in enumerate(units):
            for bed_num in range(beds_per_unit):
                bed_id = f"{unit}-{bed_num:03d}"
                
                # Check if bed exists
                result = self.conn.execute(
                    "SELECT bed_id FROM beds WHERE bed_id = ?", 
                    [bed_id]
                ).fetchone()
                
                if not result:
                    self.conn.execute("""
                        INSERT INTO beds (bed_id, unit, status, patient_id)
                        VALUES (?, ?, 'available', NULL)
                    """, [bed_id, unit])
                    
        self.conn.commit()
        
    async def store_event(self, event: Dict[str, Any]):
        """Store HL7 event in database"""
        try:
            event_id = f"{event['event_type']}_{event['patient_id']}_{datetime.utcnow().timestamp()}"
            
            self.conn.execute("""
                INSERT INTO hl7_events (id, event_type, patient_id, bed_id, timestamp, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                event_id,
                event['event_type'],
                event['patient_id'],
                event.get('bed_id'),
                datetime.utcnow(),
                json.dumps(event)
            ])
            
            # Update bed and patient tables based on event type
            if event['event_type'] == 'A01':  # Admission
                await self._handle_admission(event)
            elif event['event_type'] == 'A03':  # Discharge
                await self._handle_discharge(event)
            elif event['event_type'] == 'A02':  # Transfer
                await self._handle_transfer(event)
                
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error storing event: {e}")
            
    async def _handle_admission(self, event: Dict[str, Any]):
        """Handle patient admission"""
        # First, check if patient is already assigned to a bed
        existing_bed = self.conn.execute("""
            SELECT bed_id FROM beds WHERE patient_id = ?
        """, [event['patient_id']]).fetchone()
        
        if existing_bed:
            # Clear the existing bed assignment
            self.conn.execute("""
                UPDATE beds 
                SET status = 'available', 
                    patient_id = NULL,
                    admission_time = NULL
                WHERE patient_id = ?
            """, [event['patient_id']])
            logger.warning(f"Patient {event['patient_id']} was already in bed {existing_bed[0]}, clearing old assignment")
        
        # Update bed status
        self.conn.execute("""
            UPDATE beds 
            SET status = 'occupied', 
                patient_id = ?,
                admission_time = ?
            WHERE bed_id = ?
        """, [event['patient_id'], datetime.utcnow(), event['bed_id']])
        
        # Insert or update patient
        self.conn.execute("""
            INSERT INTO patients (patient_id, name, age, diagnosis, admission_time, discharge_status, metadata)
            VALUES (?, ?, ?, ?, ?, 'admitted', ?)
            ON CONFLICT (patient_id) DO UPDATE SET
                admission_time = ?,
                discharge_status = 'admitted'
        """, [
            event['patient_id'],
            event.get('patient_name', 'Unknown'),
            event.get('age', 0),
            event.get('diagnosis', 'Pending'),
            datetime.utcnow(),
            json.dumps(event.get('metadata', {})),
            datetime.utcnow()
        ])
        
    async def _handle_discharge(self, event: Dict[str, Any]):
        """Handle patient discharge"""
        # Update bed status
        self.conn.execute("""
            UPDATE beds 
            SET status = 'available', 
                patient_id = NULL,
                admission_time = NULL,
                expected_discharge = NULL,
                discharge_barriers = NULL
            WHERE patient_id = ?
        """, [event['patient_id']])
        
        # Update patient status
        self.conn.execute("""
            UPDATE patients 
            SET discharge_status = 'discharged'
            WHERE patient_id = ?
        """, [event['patient_id']])
        
    async def _handle_transfer(self, event: Dict[str, Any]):
        """Handle patient transfer between beds"""
        # Clear old bed
        self.conn.execute("""
            UPDATE beds 
            SET status = 'available', 
                patient_id = NULL
            WHERE patient_id = ?
        """, [event['patient_id']])
        
        # Update new bed
        self.conn.execute("""
            UPDATE beds 
            SET status = 'occupied', 
                patient_id = ?
            WHERE bed_id = ?
        """, [event['patient_id'], event['new_bed_id']])
        
    async def get_bed_status(self) -> List[Dict[str, Any]]:
        """Get current status of all beds"""
        result = self.conn.execute("""
            SELECT b.*, p.name as patient_name, p.diagnosis
            FROM beds b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            ORDER BY b.unit, b.bed_id
        """).fetchall()
        
        beds = []
        for row in result:
            bed = {
                "bed_id": row[0],
                "unit": row[1],
                "status": row[2],
                "patient_id": row[3],
                "admission_time": row[4].isoformat() if row[4] else None,
                "expected_discharge": row[5].isoformat() if row[5] else None,
                "discharge_barriers": json.loads(row[6]) if row[6] else [],
                "patient_name": row[7],
                "diagnosis": row[8]
            }
            beds.append(bed)
            
        return beds
        
    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient information"""
        result = self.conn.execute("""
            SELECT * FROM patients WHERE patient_id = ?
        """, [patient_id]).fetchone()
        
        if result:
            return {
                "patient_id": result[0],
                "name": result[1],
                "age": result[2],
                "diagnosis": result[3],
                "admission_time": result[4].isoformat() if result[4] else None,
                "discharge_status": result[5],
                "barriers": json.loads(result[6]) if result[6] else [],
                "metadata": json.loads(result[7]) if result[7] else {}
            }
        return None
        
    async def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent system alerts"""
        result = self.conn.execute("""
            SELECT * FROM alerts
            ORDER BY timestamp DESC
            LIMIT ?
        """, [limit]).fetchall()
        
        alerts = []
        for row in result:
            alerts.append({
                "id": row[0],
                "type": row[1],
                "severity": row[2],
                "message": row[3],
                "data": json.loads(row[4]) if row[4] else {},
                "timestamp": row[5].isoformat() if row[5] else None
            })
            
        return alerts
        
    async def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()