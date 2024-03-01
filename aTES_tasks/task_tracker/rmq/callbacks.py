"""
Provides callbacks for rabbitmq
"""
import aio_pika


async def consume_messages(rabbitmq_component):
    channel = await rabbitmq_component.get_channel()
    queue = await channel.declare_queue('test')

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print("Received message:", message.body.decode())


async def send_message(request, rabbitmq_component):
    data = await request.json()

    channel = await rabbitmq_component.get_channel()

    await channel.default_exchange.publish(
        aio_pika.Message(body=str(data).encode()),
        routing_key='all_events'
    )

    # return web.Response(text="Message sent to 'all_events' exchange")
