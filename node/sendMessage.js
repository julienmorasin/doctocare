function sendMessage (topicName, data) {
  // Instantiates a client
  const PubSub = require('@google-cloud/pubsub');
  const pubsub = PubSub();

  // References an existing topic, e.g. "my-topic"
  const topic = pubsub.topic(topicName);

  // Publishes the message, e.g. "Hello, world!" or { amount: 599.00, status: 'pending' }
  return topic.publish(data)
    .then((results) => {
      const messageIds = results[0];

      console.log(`Message ${messageIds[0]} published.`);

      return messageIds;
    });
}

sendMessage('userUpdate', 'Bonjour User !');
