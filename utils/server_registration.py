import os
from spacetime import Node
from utils.pcc_models import Register

def init(df, user_agent, fresh):
    reg = df.read_one(Register, user_agent)
    if not reg:
        reg = Register(user_agent, fresh)
        df.add_one(Register, reg)
        df.commit()
        df.push_await()
    while not reg.load_balancer:
        df.pull_await()
        if reg.invalid:
            raise RuntimeError("User agent string is not acceptable.")
        if reg.load_balancer:
            df.delete_one(Register, reg)
            df.commit()
            df.push()
    return reg.load_balancer


def check_server_reachable(host, port):
    import socket
    try:
        # Try to establish a connection
        # TODO: check cache service is available or not
        with socket.create_connection((host, port), timeout=5):
            print(f"Server {host}:{port} is reachable.")
            return True
    except (socket.timeout, socket.error):
        print(f"Server {host}:{port} is not reachable.")
        return False

def get_cache_server(config, restart):
    check_server_reachable(config.host, config.port)
    init_node = Node(
        init, Types=[Register], dataframe=(config.host, config.port))
    return init_node.start(
        config.user_agent, restart or not os.path.exists(config.save_file))