from json import load


def get_websocket_server_settings():
    with open('../websocket_settings.json', 'r') as reader:
        websocket_server_settings = load(reader)
    host = websocket_server_settings['host']
    port = websocket_server_settings['port']
    ws_uri = f'ws://{host}:{port}/ws'

    return ws_uri, host, port
