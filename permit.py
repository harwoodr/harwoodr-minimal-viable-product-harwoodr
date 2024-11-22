#!/usr/bin/env python
import pika

#change the credentials to match your RabbitMQ credentials
credentials = pika.PlainCredentials('admin', 'cas735')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost",credentials=credentials),
)
channel = connection.channel()

channel.queue_declare(queue="permit_queue")

def on_request(ch, method, props, body):
    #activated when a permit validation request shows up on the message queue
    transponder = int(body)
    print(f"\n [x] Transponder {transponder} received for permit validation")    
    response = validate(transponder)
    print(f" [x] Has {response} permit")

    #send response to the requester return message queue
    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=str(response),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

def lookup(transponder):
    #a list will do as a proxy for a database
    permits = [1,3,5,7]
    if transponder in permits:
        return True
    else:
        return False

def validate(transponder):
    #business logic to determine validity - it's very complex...
    if lookup(transponder):
        return "valid"
    else:
        return "invalid"


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="permit_queue", on_message_callback=on_request)

print(" [x] Watching message queue for permit validation requests")
#if we wanted to support other adapters, we'd use a non-blocking queue consumer here in a loop - but for the MVP this is fine
channel.start_consuming()

