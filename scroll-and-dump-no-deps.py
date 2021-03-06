#!/usr/local/bin/python3
import json
import urllib.request

ES_HOST = 'http://localhost:9200'
ES_USER = 'elastic'
ES_PASSWORD = 'elastic'
INDEX_TO_DUMP = 'kibana_sample_data_ecommerce'
OUT_FILE = '/tmp/dump-example2.txt'


def dump_hits(hits, out_file):
    for hit in hits:
        out_file.write(f"{json.dumps(hit['_source'])}\n")


def scroll_and_dump():

    top_level_url = f'{ES_HOST}'

    # create a password manager and add username and password
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, top_level_url, ES_USER, ES_PASSWORD)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

    # create "opener" (OpenerDirector instance)
    opener = urllib.request.build_opener(handler)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    request_body = '{"query": {"match_all": {}}}'.encode("utf-8")

    url = f'{ES_HOST}/{INDEX_TO_DUMP}/_search?scroll=1m'
    req = urllib.request.Request(url, request_body, headers)
    response = opener.open(req)
    data = json.loads(response.read().decode("utf-8"))
    
    # Get the scroll ID
    sid = data['_scroll_id']
    scroll_size = len(data['hits']['hits'])

    with open(OUT_FILE, 'w') as out_file:
        # Before scroll, process current batch of hits
        dump_hits(data['hits']['hits'], out_file)

        while scroll_size > 0:

            scroll_json = {
                "scroll": "1m",
                "scroll_id": sid
            }
            request_body = json.dumps(scroll_json).encode("utf-8")

            url = f'{ES_HOST}/_search/scroll'
            req = urllib.request.Request(url, request_body, headers)
            response = opener.open(req)
            data = json.loads(response.read().decode("utf-8"))

            # Process current batch of hits
            dump_hits(data['hits']['hits'], out_file)

            # Update the scroll ID
            sid = data['_scroll_id']

            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])


if __name__ == "__main__":
    scroll_and_dump()
