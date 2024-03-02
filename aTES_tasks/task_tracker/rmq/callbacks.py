"""
Provides callbacks for rabbitmq
"""
import aio_pika


async def user_callback(message, data):
    message_body = message['body']
    print(message_body)
    print(data)
    # event = message_body['event']
    # user = message_body['object']
    # app = data
    # print(event, user)


async def send_message(request, rabbitmq_component):
    data = await request.json()

    channel = await rabbitmq_component.get_channel()

    await channel.default_exchange.publish(
        aio_pika.Message(body=str(data).encode()),
        routing_key='all_events'
    )

    # return web.Response(text="Message sent to 'all_events' exchange")
