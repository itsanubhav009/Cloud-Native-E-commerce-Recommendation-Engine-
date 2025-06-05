import json
from typing import Dict, Any
from kafka import KafkaProducer
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EventProducer:
    def __init__(self):
        self.producer = None
        self.connected = False
        self.connect()
    
    def connect(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda v: v.encode('utf-8') if v else None,
                acks='all',
                retries=3
            )
            self.connected = True
            logger.info("Successfully connected to Kafka")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {str(e)}")
            self.connected = False
    
    def send_event(self, event_type: str, data: Dict[str, Any], key: str = None):
        if not self.connected:
            self.connect()
            if not self.connected:
                logger.error("Cannot send event: not connected to Kafka")
                return False
        
        try:
            # Prepare event payload
            event_payload = {
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to Kafka
            future = self.producer.send(
                settings.KAFKA_TOPIC_EVENTS,
                key=key,
                value=event_payload
            )
            
            # Wait for the result
            record_metadata = future.get(timeout=10)
            logger.info(f"Event sent to {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send event to Kafka: {str(e)}")
            return False

# Singleton instance
event_producer = EventProducer()