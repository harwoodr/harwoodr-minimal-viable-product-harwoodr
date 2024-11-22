#!/usr/bin/env python
import uuid
import os
import sys
import pika
import random
import time

#RpcClient is both our inbound and outbound adapter for AMQP
class RpcClient(object):
    def __init__(self):
        #change the credentials to match your RabbitMQ credentials
        credentials = pika.PlainCredentials('admin', 'cas735')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost",credentials=credentials),
        )

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

        self.response = None
        self.corr_id = None
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
            
    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange="",
            routing_key="permit_queue",
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n),
        )
        self.connection.process_data_events(time_limit=None)
        return (self.response)

    
def scan():
    #press key to simulate transponder at gate
    print("Enter a value from 0-9 to represent a transponder - Some are connected to valid permits and some are not")
    print("...and press enter.")
    selection = "-1"
    values = list(map(str, [*range(0,10,1)]))
    while (selection not in values):
        selection = input("input:")
    return selection

def validate(transponder):
    #submit a request to determine if there is a valid permit associated with the transponder
    gate_rpc = RpcClient()
    print(f"\n [x] Sending {transponder} for permit validation")
    #get the validation response from the message queue
    response = gate_rpc.call(transponder)
    return response


def evaluate(response):
    #if the permit is valid, send the command to open the gate
    response = response.decode()
    if response == "valid":
        print(f" [x] Permit for transponder is valid")
        gate()
    else:
        print(f" [x] Permit for transponder is invalid")

def gate():
    #simulates opening the gate
    print(" [x] the gate opens and allows one car through")

def main():
    
    while True:
        if len(sys.argv)>1 and sys.argv[1]=="auto":
            selection = random.randint(0,9)
            time.sleep(1)
            print(f" [x] Transponder {selection} read at gate")
        else:
            selection = scan()

        response = validate(selection)
        
        evaluate(response)
            
        print();

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

