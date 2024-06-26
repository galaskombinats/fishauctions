import json
from channels.generic.websocket import WebsocketConsumer

class AuctionConsumer(WebsocketConsumer):
    def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.auction_group_name = f'auction_{self.auction_id}'

        # Join auction group
        self.channel_layer.group_add(
            self.auction_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave auction group
        self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        bid_amount = data['bid']

        # Send message to auction group
        self.channel_layer.group_send(
            self.auction_group_name,
            {
                'type': 'auction_bid',
                'bid': bid_amount
            }
        )

    # Receive message from auction group
    def auction_bid(self, event):
        bid_amount = event['bid']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'bid': bid_amount
        }))
