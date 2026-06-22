import json

from aiokafka import AIOKafkaConsumer

from app.config import settings
from app.schemas import KafkaEvent
from app.router import route_event


class KafkaEventConsumer:

    def __init__(self):
        topics = settings.KAFKA_CONSUME_TOPIC.split(",");
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_GROUP_ID,
            auto_offset_reset="earliest",
        );

    async def start(self):
        await self.consumer.start();

        try:
            async for message in self.consumer:
                await self.process_message(message.value);

        finally:
            await self.consumer.stop();

    async def process_message(self, raw_message: bytes):
        try:
            payload = json.loads(raw_message.decode());

            event = KafkaEvent(**payload);

            await route_event(event);

        except Exception as exc:
            print(f"Failed to process message: {exc}");
