from myapp import create_app
from myapp.database import db, Message, ChatMessage
from flask_socketio import SocketIO, emit, join_room, leave_room

app = create_app()  # Only return the app here
socket = SocketIO(app)  # Initialize SocketIO with the app

# COMMUNICATION ARCHITECTURE

# Join-chat event. Emit online message to other users and join the room
@socket.on("join-chat")
def join_private_chat(data):
    room = data["rid"]
    join_room(room=room)
    socket.emit(
        "joined-chat",
        {"msg": f"{room} is now online."},
        room=room,
        # include_self=False,
    )


# Outgoing event handler
@socket.on("outgoing")
def chatting_event(json, methods=["GET", "POST"]):
    """
    Handles saving messages and sending messages to all clients
    :param json: json
    :param methods: POST, GET
    :return: None
    """
    room_id = json["rid"]
    timestamp = json["timestamp"]
    message = json["message"]
    sender_id = json["sender_id"]
    sender_username = json["sender_username"]

    # Get the message entry for the chat room, create one if it doesn't exist
    message_entry = Message.query.filter_by(room_id=room_id).first()

    if not message_entry:
        # If no entry exists, create a new message entry for the room
        message_entry = Message(room_id=room_id)
        db.session.add(message_entry)
        db.session.commit()

    # Create a new ChatMessage instance
    chat_message = ChatMessage(
        content=message,
        timestamp=timestamp,
        sender_id=sender_id,
        sender_username=sender_username,
        room_id=room_id,
    )

    # Add the new chat message to the messages relationship of the message
    message_entry.messages.append(chat_message)

    # Commit the new message to the database
    try:
        db.session.add(chat_message)
        db.session.commit()
    except Exception as e:
        # Handle the database error
        print(f"Error saving message to the database: {str(e)}")
        db.session.rollback()

    # Emit the message(s) sent to other users in the room
    socket.emit(
        "message",
        json,
        room=room_id,
        include_self=False,
    )


if __name__ == "__main__":
    socket.run(app, allow_unsafe_werkzeug=True, debug=True)
