from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import asyncio
import logging
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)


class HL7Consumer:
    def __init__(self):
        self.bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        self.topic = 'hl7-events'
        self.consumer = None
        self._initialize_consumer()
        
    def _initialize_consumer(self):
        """Initialize Kafka consumer with retry logic"""
        max_retries = 10
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.bootstrap_servers,
                    auto_offset_reset='latest',
                    enable_auto_commit=True,
                    group_id='pcc-consumer-group',
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    consumer_timeout_ms=1000  # 1 second timeout for poll
                )
                logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
                break
            except Exception as e:
                logger.warning(f"Failed to connect to Kafka (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                else:
                    logger.error("Failed to connect to Kafka after all retries")
                    raise
                    
    def consume_events_sync(self) -> List[Dict[str, Any]]:
        """Synchronous version of consume_events for executor"""
        return self.consume_events()
        
    def consume_events(self) -> List[Dict[str, Any]]:
        """Consume HL7 events from Kafka"""
        events = []
        
        try:
            # Use poll to get messages with timeout
            message_batch = self.consumer.poll(timeout_ms=1000, max_records=10)
            
            for topic_partition, messages in message_batch.items():
                for message in messages:
                    try:
                        event = message.value
                        logger.info(f"Received HL7 event: {event['event_type']} for patient {event['patient_id']}")
                        events.append(event)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
            # Try to reinitialize consumer
            self._initialize_consumer()
        except Exception as e:
            logger.error(f"Unexpected error consuming events: {e}")
            
        return events
        
    def close(self):
        """Close Kafka consumer"""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")