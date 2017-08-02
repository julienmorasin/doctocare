function receiveMessages (subscriptionName) {
  // Instantiates a client
  const PubSub = require('@google-cloud/pubsub');
  const pubsub = PubSub();

  // References an existing subscription, e.g. "my-subscription"
  const subscription = pubsub.subscription(subscriptionName);

  // Pulls messages. Set returnImmediately to false to block until messages are
  // received.
  return subscription.pull()
    .then((results) => {
      const messages = results[0];

      console.log(`Received ${messages.length} messages.`);

      messages.forEach((message) => {
        console.log(`* %d %j %j`, message.id, message.data, message.attributes);
      });

      // Acknowledges received messages. If you do not acknowledge, Pub/Sub will
      // redeliver the message.
      return subscription.ack(messages.map((message) => message.ackId));
    });
}

receiveMessages('subUserUpdate');
