from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from typing import Dict, Any
import os
import time

logger = logging.getLogger(__name__)


class HL7Producer:
    def __init__(self):
        self.bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        self.topic = 'hl7-events'
        self.producer = None
        self._initialize_producer()
        
    def _initialize_producer(self):
        """Initialize Kafka producer with retry logic"""
        max_retries = 10
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    acks='all',
                    retries=3,
                    max_in_flight_requests_per_connection=1
                )
                logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
                break
            except Exception as e:
                logger.warning(f"Failed to connect to Kafka (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("Failed to connect to Kafka after all retries")
                    raise
                    
    async def send_event(self, event: Dict[str, Any]):
        """Send HL7 event to Kafka"""
        import asyncio
        try:
            # Run the sync operation in a thread pool
            loop = asyncio.get_event_loop()
            future = await loop.run_in_executor(
                None, 
                lambda: self.producer.send(self.topic, event).get(timeout=10)
            )
            logger.info(f"Sent HL7 event to topic {self.topic} partition {future.partition if hasattr(future, 'partition') else 0}")
        except KafkaError as e:
            logger.error(f"Failed to send event: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending event: {e}")
            raise
            
    def flush(self):
        """Flush any pending messages"""
        if self.producer:
            self.producer.flush()
            
    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")