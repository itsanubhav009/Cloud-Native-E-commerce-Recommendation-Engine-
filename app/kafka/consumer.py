import json
from kafka import KafkaConsumer
from app.core.config import settings
import threading
import logging
from app.ml.recommender import update_recommendations
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

class EventConsumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.daemon = True
        
    def stop(self):
        self.stop_event.set()
        
    def run(self):
        try:
            consumer = KafkaConsumer(
                settings.KAFKA_TOPIC_EVENTS,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='recommendation_processor',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            logger.info("Kafka consumer started successfully")
            
            while not self.stop_event.is_set():
                for message in consumer:
                    if self.stop_event.is_set():
                        break
                    
                    try:
                        # Process the event
                        event = message.value
                        event_type = event.get('event_type')
                        data = event.get('data', {})
                        
                        logger.info(f"Processing event: {event_type}")
                        
                        # Create a new DB session for this event
                        db = SessionLocal()
                        try:
                            if event_type in ['view', 'purchase', 'cart_add']:
                                # Update recommendations based on user activity
                                user_id = data.get('user_id')
                                product_id = data.get('product_id')
                                
                                if user_id and product_id:
                                    update_recommendations(db, user_id, product_id, event_type)
                            
                        finally:
                            db.close()
                            
                    except Exception as e:
                        logger.error(f"Error processing Kafka message: {str(e)}")
            
            consumer.close()
            
        except Exception as e:
            logger.error(f"Kafka consumer error: {str(e)}")