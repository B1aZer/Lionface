Lionface is a startup focused primary on nonprofit organizations and social interactions. This project is a result of 9 months work in collaboration with Nick Clark as a designer and a founder.

Server code is written in python with the help of the django framework. MySQL was chosen as the main database. Redis is used as a support key-value storage for it's simplicity and pub/sub functional. To achieve seamless client/server interaction SocketIO was used. Gunicorn with gevent are backing up socketio on the server side, while jQuery simplifies most user actions. One of the Shortest path algorithms was utilized in this project. Lionface is hosted on Amazon EC2 and uses RDS as database storage.

