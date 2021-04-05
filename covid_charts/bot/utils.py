def is_sender_admin(message, bot):
    user = message.from_user
    if message.chat.type != 'private':
        # get chat member and user group info
        chatmember = bot.get_chat_member(message.chat.id, user.id)
        if(chatmember.status == 'administrator' or chatmember.status == 'creator'):
            return True
        else:
            return False
    else:
        return True
