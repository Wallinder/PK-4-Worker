class opcodes:
    DISPATCH	                = 0  #  Receive       An event was dispatched.
    HEARTBEAT	                = 1  #  Send/Receive  Fired periodically by the client to keep the connection alive.
    IDENTIFY	                = 2  #  Send	      Starts a new session during the initial handshake.
    PRESENCE_UPDATE             = 3  #  Send          Update the client's presence.
    VOICE_STATE_UPDATE          = 4  #  Send          Used to join/leave or move between voice channels.
    RESUME                      = 6  #  Send          Resume a previous session that was disconnected.
    RECONNECT                   = 7  #  Receive       You should attempt to reconnect and resume immediately.
    REQUEST_GUILD_MEMBERS       = 8  #  Send          Request information about offline guild members in a large guild.
    INVALID_SESSION             = 9  #  Receive       The session has been invalidated. You should reconnect and identify/resume accordingly.
    HELLO                       = 10 #  Receive       Sent immediately after connecting, contains the heartbeat_interval to use.
    HEARTBEAT_ACK               = 11 #  Receive       Sent in response to receiving a heartbeat to acknowledge that it has been received.
    REQUEST_SOUNDBOARD_SOUNDS   = 31 #  Send          Request information about soundboard sounds in a set of guilds.
