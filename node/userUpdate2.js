// Connection informations & Requirements
const projectId = 'projet-test-doctegestio';
const PubSub = require('@google-cloud/pubsub');
var fs = require('fs');
var readline = require('readline');
var google = require('googleapis');
var googleAuth = require('google-auth-library');
var googleSpreadsheet = require('google-spreadsheet');
var service = google.admin('directory_v1');
var retreivedUsers = [];

// If modifying these scopes, delete your previously saved credentials
// at ~/.credentials/admin-directory_v1-nodejs-quickstart.json
var SCOPES = ['https://www.googleapis.com/auth/admin.directory.user'];
var TOKEN_DIR = (process.env.HOME || process.env.HOMEPATH ||
    process.env.USERPROFILE) + '/.credentials/';
var TOKEN_PATH = TOKEN_DIR + 'admin-directory_v1-nodejs-quickstart.json';

// Load client secrets from a local file.
fs.readFile('client_secret.json', function processClientSecrets(err, content) {
  if (err) {
    console.log('Error loading client secret file: ' + err);
    return;
  }
  // Authorize a client with the loaded credentials, then call the
  // Directory API.
  authorize(JSON.parse(content), retreiveUsers);
});

/**
 * Create an OAuth2 client with the given credentials, and then execute the
 * given callback function.
 *
 * @param {Object} credentials The authorization client credentials.
 * @param {function} callback The callback to call with the authorized client.
 */
function authorize(credentials, callback) {
  var clientSecret = credentials.installed.client_secret;
  var clientId = credentials.installed.client_id;
  var redirectUrl = credentials.installed.redirect_uris[0];
  var auth = new googleAuth();
  var oauth2Client = new auth.OAuth2(clientId, clientSecret, redirectUrl);

  // Check if we have previously stored a token.
  fs.readFile(TOKEN_PATH, function(err, token) {
    if (err) {
      getNewToken(oauth2Client, callback);
    } else {
      oauth2Client.credentials = JSON.parse(token);
      callback(oauth2Client);
    }
  });
}

/**
 * Get and store new token after prompting for user authorization, and then
 * execute the given callback with the authorized OAuth2 client.
 *
 * @param {google.auth.OAuth2} oauth2Client The OAuth2 client to get token for.
 * @param {getEventsCallback} callback The callback to call with the authorized
 *     client.
 */
function getNewToken(oauth2Client, callback) {
  var authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES
  });
  console.log('Authorize this app by visiting this url: ', authUrl);
  var rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  rl.question('Enter the code from that page here: ', function(code) {
    rl.close();
    oauth2Client.getToken(code, function(err, token) {
      if (err) {
        console.log('Error while trying to retrieve access token', err);
        return;
      }
      oauth2Client.credentials = token;
      storeToken(token);
      callback(oauth2Client);
    });
  });
}

/**
 * Store token to disk be used in later program executions.
 *
 * @param {Object} token The token to store to disk.
 */
function storeToken(token) {
  try {
    fs.mkdirSync(TOKEN_DIR);
  } catch (err) {
    if (err.code != 'EEXIST') {
      throw err;
    }
  }
  fs.writeFile(TOKEN_PATH, JSON.stringify(token));
  console.log('Token stored to ' + TOKEN_PATH);
}

function retreiveUsers(auth, pageToken = ''){
    var listObject = {
            customer: 'my_customer',
            maxResults: 500,
            auth: auth,
            orderBy: 'email',
            pageToken: pageToken
            };

    var nextPageToken = '',
        listUsers = [];


    service.users.list(listObject, function getUsers(err, response) {
        if (err) {
          console.log('The API returned an error: ' + err);
          return;
        }

        var users = response.users;
        if (users.length == 0) {
          console.log('No users in the domain.');
        } else {
          for (var i = 0; i < users.length; i++) {
            var user = users[i];
            listUsers.push(user);
          }
        }

        nextPageToken = response.nextPageToken;

        if (nextPageToken && nextPageToken !== '') {
          listObject.pageToken = nextPageToken;
          retreiveUsers(auth, nextPageToken);
          console.log('running..');
      }else{
          console.log('All users retreived !');
          retreivedUsers = listUsers;

      }

    });

}

function writeToSpreadsheet(){
    console.log(retreivedUsers);
}
function sendMessage (topicName, data) {
  // Instantiates a client
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

function receiveMessages (subscriptionName) {
  // Instantiates a client
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
