import socket
import threading
import time

PORT = 7447

# message size in bytes
MESSAGE_LENGTH_SIZE = 64

# encoding method
ENCODING = 'utf-8'


# s = socket.socket("NETWORK LAYER PROTOCOL", "TRANSPORT LAYER PROTOCOL")
# s.connect("HOST INFORMATION")
# s.send()
#message format :: "method:username:to:kind:T(isFile):message"

username = ''

def main():
    global username
    # address = socket.gethostbyname(socket.gethostname())
    SERVER_INFORMATION = ('localhost', PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(SERVER_INFORMATION)
    t = threading.Thread(target=get_messages)
    t.start()
    flag = True
    while True:
        req = input('type your request by format --> method:username:to:kind:T(isFile):message\n')
        if req == 'file':
            send_msg(s, req)
            receive_file()
            continue
        pa = req.split(':')
        if not pa[1] == '' and flag:
            username = pa[1]
            flag = False
        elif pa[1] == '' and flag:
            print("an error occurred")
            s.close()
            break
        send_msg(s, req)
        if pa[5] == 'DISCONNECT':
            s.close()
            break
        parser(s,"server response : ")
        # send_msg(s, "HELLO WORLD!!")
        # send_msg(s, "DISCONNECT")

def get_messages():
    SERVER_INFORMATION = ('localhost', PORT)
    se = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    se.connect(SERVER_INFORMATION)
    while True:
        if username == '':
            continue
        send_msg(se, "get:"+username+"::message:0:")
        parser(se,"my messages :: ")
        time.sleep(3)

def parser(s,desc):
    message_length = int(s.recv(MESSAGE_LENGTH_SIZE).decode(ENCODING))
    msg = s.recv(message_length).decode(ENCODING)
    if not "not found any thing" in msg:
        print(desc+msg)

def send_msg(client, msg):
    message = msg.encode(ENCODING)

    msg_length = len(message)
    msg_length = str(msg_length).encode(ENCODING)
    # adding padding to make the message length equal to the set amount
    msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))

    client.send(msg_length)
    client.send(message)


def receive_file():
    se = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    se.bind(('localhost', 9989))
    conn, addr = se.accept()
    with open('received_file', 'wb') as file:
        print("[DOWNLOADING FILE]")
        while True:
            print("[DOWNLOADING FILE STARTED]")
            sliver = conn.recv(1024)
            if not sliver:
                break
            file.write(sliver)
    file.close()
    print("[FILE DOWNLOADED SUCCESSFULLY]")
    conn.close()
    se.close()


# not tested
def change_username(current_username, username_to_be, socket):
    cmd = str("[CHANGE USERNAME]" + "/" +
              current_username + "/" + username_to_be)
    send_msg(socket, cmd)


if __name__ == '__main__':
    main()
