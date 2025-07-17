import socket
import json
import time
txt="""
============================
工程:虛擬貨幣挖礦V2.5
工作室:情雲工作室
項目負責:魚生
項目指揮:情雲
============================
"""
print(txt)
def send_stratum_request(sock, id_num, method, params):
    msg = {
        "id": id_num,
        "method": method,
        "params": params
    }
    msg_str = json.dumps(msg) + "\n"
    sock.sendall(msg_str.encode('utf-8'))
    print(f"送出訊息: {msg_str.strip()}")

def connect_and_mine(pool_host, pool_port, wallet, password):
    reconnect_delay = 5
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                print(f"連接礦池 {pool_host}:{pool_port} ...")
                sock.connect((pool_host, pool_port))
                print("連線成功！")

                send_stratum_request(sock, 1, "mining.subscribe", [])

                authorized = False
                auth_attempts = 0
                max_auth_attempts = 3

                while not authorized and auth_attempts < max_auth_attempts:
                    auth_attempts += 1
                    print(f"嘗試授權 第 {auth_attempts} 次...")
                    send_stratum_request(sock, 2, "mining.authorize", [wallet, password])
                    sock.settimeout(5)
                    try:
                        data = sock.recv(4096)
                        if not data:
                            print("伺服器斷線了")
                            break
                        msg = json.loads(data.decode().strip())
                        print("收到訊息:", msg)
                        if msg.get("id") == 2:
                            if msg.get("result") is True:
                                print("授權成功！")
                                authorized = True
                            else:
                                print("授權失敗，將重試！")
                    except socket.timeout:
                        print("授權回應超時，將重試！")
                    except json.JSONDecodeError:
                        print("收到無效授權回應，將重試！")

                if not authorized:
                    print(f"授權連續失敗 {max_auth_attempts} 次，5秒後重連...")
                    time.sleep(reconnect_delay)
                    continue

                sock.settimeout(1)
                buffer = ""
                while True:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            print("伺服器斷線了")
                            break

                        buffer += data.decode()
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            if line.strip() == "":
                                continue
                            try:
                                msg = json.loads(line)
                                print("收到訊息:", msg)
                            except json.JSONDecodeError:
                                print("收到無效JSON訊息")

                    except socket.timeout:
                        time.sleep(0.1)

        except Exception as e:
            print(f"連線出錯: {e}")
            print(f"{reconnect_delay}秒後嘗試重連")
            time.sleep(reconnect_delay)

def main():
    pool_host = input("請輸入礦池主機:")
    pool_port = int(input("請輸入礦池連接埠:"))
    wallet = input("請輸入錢包地址(帳號):")
    password = input("請輸入礦池密碼如果沒有就打x:")

    connect_and_mine(pool_host, pool_port, wallet, password)

if __name__ == "__main__":
    main()
