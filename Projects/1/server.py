import socket
import threading

groupCount = 0
users = {}  # {"username":{"groups":[]}} groups is set
messages = {}  # {"username":[["message","isFile"]]}

PORT = 7447

# message size in bytes
MESSAGE_LENGTH_SIZE = 64

# encoding method
ENCODING = 'utf-8'


def main():
    global s
    # address = socket.gethostbyname(socket.gethostname())
    # print(address)
    HOST_INFORMATION = ('localhost', PORT)
    # SOCK_STREAM = TCP, SOCK_DGRAM = UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(HOST_INFORMATION)

    print("[SERVER STARTS] Server is starting ...")

    start(s)


# initializing the server
def start(server):
    server.listen()
    while True:
        conn, address = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, address))
        t.start()


# message format :: "method:username:to:kind:1(isFile):message"
#                      0     1       2   3     4        5
def handle_client(conn, address):
    print("[NEW CONNECTION] Connected from {}".format(address))

    Connected = True

    while Connected:
        message_length = int(conn.recv(MESSAGE_LENGTH_SIZE).decode(ENCODING))

        msg = conn.recv(message_length).decode(ENCODING)
        if isinstance(msg, str) and msg == 'file':
            send_file()
        else:
            msg = str.split(msg, ':')
            # print("[MESSAGE RECEIVED] {}".format(msg))
            if msg[5] == "DISCONNECT":
                Connected = False
            if msg[0] == 'post' or msg[0] == 'get' or msg[0] == 'put':
                if msg[0] == 'post':
                    if msg[2] == '' and msg[3] == '':
                        response(change_username(msg[1]), conn)
                    if not has_key(msg[1], users):
                        response("ERROR! you're username not found", conn)
                    elif msg[2] == '' and msg[3] == 'group':
                        response(create_group(msg[1], str.split(msg[5], ',')), conn)
                    elif not msg[2] == '' and msg[3] == 'group':
                        response(send_message(msg[1], msg[5], msg[2], msg[4], True), conn)
                    elif not msg[2] == '' and msg[3] == 'message':
                        response(send_message(msg[1], msg[5], msg[2], msg[4], False), conn)
                elif msg[0] == 'get':
                    if not has_key(msg[1], users):
                        response("ERROR! you're username not found", conn)
                    if msg[4] == '0' and msg[3] == 'message':
                        response(get_messages(msg[1]), conn)
                    elif msg[4] == '0' and msg[3] == 'groups':
                        response(get_groups(msg[1]), conn)
                elif msg[0] == 'put':
                    if not has_key(msg[1], users):
                        response("ERROR! you're username not found", conn)
                    if msg[2] == '' and msg[3] == '' and not msg[5] == '':
                        response(change_username(msg[1], msg[5]), conn)
    conn.close()


# not tested
def send_file(filename='server-sample'):
    se = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    se.connect(('localhost', 9989))
    try:
        file = open(filename, 'rb')
        print("[SENDING FILE] {}".format(filename))
    except:
        print("[SENDING FILE FAILED] {}".format(filename))
    sliver = file.read(1024)

    while True:
        se.send(sliver)
        sliver = file.read(1024)
        if not sliver:
            break
    file.close()
    print("[FILE SENT SUCCESSFULLY] {}".format(filename))
    se.close()


def response(message, socket):
    re = ''
    if isinstance(message, str):
        re = message + "-0,"
    else:
        for m in message:
            re = re + m[0] + "-" + m[1] + ","

    me = re.encode(ENCODING)
    msg_length = len(me)
    msg_length = str(msg_length).encode(ENCODING)
    msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))
    socket.send(msg_length)
    socket.send(me)


def change_username(current_username, enterred_username=None):
    if enterred_username == None:
        if has_key(current_username, users):
            return "ERROR!.this username already exists"
        users[current_username] = {"groups": []}
        return "you're signed up"
    else:
        if current_username != enterred_username and has_key(current_username, users) and not has_key(enterred_username,
                                                                                                      users):
            users[enterred_username] = users[current_username]
            del users[current_username]
            return "changed you're username successfully"
        else:
            return "ERROR!.you're entered username already exists"


def create_group(main, us):
    global groupCount
    for u in us:
        if has_key(u, users):
            users[u]["groups"].append(groupCount + 1)
    users[main]["groups"].append(groupCount + 1)
    groupCount = groupCount + 1
    return "created group successfully"


def get_groups(username):
    el = ''
    for e in users[username]["groups"]:
        el = el + str(e) + ","
    return el


def send_message(username, message, to, isFile, isGp=False):
    gp_exists = False
    if isGp:
        for user in users:
            for gp in users[user]['groups']:
                if int(gp) == int(to):
                    gp_exists = True
                    if not has_key(user, messages):
                        messages[user] = []
                    messages[user].append([message, isFile])


        if not gp_exists:
            return "ERROR!.not found any group related to you"


    else:
        if not has_key(to, users):
            return "ERROR!.not found any user"
        if not has_key(to, messages):
            messages[to] = []
        messages[to].append([message, isFile])
    return "sent message successfully"


def get_messages(username):
    if not has_key(username, messages):
        return "not found any thing"
    res = messages[username]
    del messages[username]
    return res


def has_key(k, arr):
    for i in arr:
        if i == k:
            return True
    return False


if __name__ == '__main__':
    main()
