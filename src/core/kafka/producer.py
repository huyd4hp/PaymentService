from aiokafka import AIOKafkaProducer
from typing import Any

class KafkaProducer:
    def __init__(self,KAFKA_BOOTSTRAP_SERVERS:str):
        self.producer = AIOKafkaProducer(
            client_id = "EventService",
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        )
    async def connect(self):
        await self.producer.start()
    async def close(self):
        await self.producer.stop()     
    async def sendMessage(self,Topic:Any,Key:Any = None,Message:Any=None):
        await self.producer.send_and_wait(
            topic = Topic,
            value = Message,
            key = Key,
        )