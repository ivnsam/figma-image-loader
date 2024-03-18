#!/usr/bin/env pyhon
import http.client
import ssl
import json
import os
import argparse
import logging

LOGGING_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

FORMATS = {
    'jpg': 'jpg', 
    'png': 'png', 
    'svg': 'svg', 
    'pdf': 'pdf',
}

def get_nodes(token: str, file_id: str):
    """
    Retrieve information about a Figma file using the Figma API.
    """

    logging.debug("Getting info about Figma file")

    conn = http.client.HTTPSConnection('api.figma.com', context=ssl._create_unverified_context())
    headers = {
        'X-FIGMA-TOKEN': token,
    }
    
    # Send a GET request to the Figma API to retrieve file details
    conn.request('GET', '/v1/files/{}'.format(file_id), headers=headers)
    response = conn.getresponse()

    # Check response status code
    if response.status != 200:
        logging.critical("Failed to retrieve the file. Status code: {}".format(response.status))
        conn.close()
        os._exit(1)
    nodes = response.readline().decode()

    conn.close()
    return nodes

def get_img_link(token: str, file_id: str, node_id: str, format: str):
    """
    Retrieve a download link for an image from the Figma API.
    """

    logging.debug("Getting link to download image")

    conn = http.client.HTTPSConnection('api.figma.com', context=ssl._create_unverified_context())
    headers = {
        'X-FIGMA-TOKEN': token,
    }
    
    # Send a GET request to the Figma API to retrieve image URLs
    conn.request('GET', '/v1/images/{}?ids={}&format={}'.format(file_id, node_id, format), headers=headers)
    response = conn.getresponse().readline().decode()
    conn.close()
    
    # Parse the JSON response to extract the image URL
    link_dict = json.loads(response)["images"].values()
    link = list(link_dict)[0]
    return link

def get_img(full_url: str, image_path: str, image_name: str, image_format: str):
    """
    Download an image by URL from the Figma API.
    """

    logging.debug("Downloading image: {}: {}".format(image_name, full_url))
    # Define the target URL and the output file name
    full_url = full_url
    url = full_url.split('//')[1].split('/')[0]
    path = full_url.split(url)[1]
    output_file = "{}/{}.{}".format(image_path, image_name, image_format)

    conn = http.client.HTTPSConnection(url, context = ssl._create_unverified_context())
    conn.request("GET", path)
    response = conn.getresponse()

    # Check if the request was successful
    if response.status == 200:
        with open(output_file, 'wb') as file:
            file.write(response.read())
    else:
        logging.critical("Failed to retrieve the file. Status code: {}".format(response.status))
        os._exit(1)

    conn.close()

def find_values(id, json_string):
    """
    Searches JSON-objects in JSON-string `json_repr` contained `id` field, collects this objects to array and returns this array.
    """
    
    logging.debug("Searching image objects in JSON")
    results = []

    def _decode_dict(a_dict):
        try:
            if id in a_dict.keys():
                results.append((a_dict["id"], a_dict["name"]))
        except KeyError:
            pass
        return a_dict

    json.loads(json_string, object_hook=_decode_dict) # Return value ignored.
    return results


if __name__ == "__main__":
    print("#########################")
    print("##  image loader v0.1  ##")
    print("#########################")

    parser = argparse.ArgumentParser(description="Image loader v0.1")
    parser.add_argument("-t", "--token", required=True, help="Your personal sccess token")
    parser.add_argument("-f", "--file", required=True, metavar="FILE_ID", help="File ID")
    parser.add_argument("-p", "--path", required=True, metavar="OUTPUT_DIR", help="Directory (or relative path) to save iamges")
    parser.add_argument("--format", choices=FORMATS.keys(), type=lambda s: s.lower(), default="svg", help="Format of the images (default: svg)")
    parser.add_argument('-l', '--loglevel', choices=LOGGING_LEVELS.keys(), type=lambda s: s.upper(), default='INFO', help='Set logging level (default: INFO)')
    args = parser.parse_args()

    # Configure the logging module
    logging.basicConfig(
        level=LOGGING_LEVELS[args.loglevel], 
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    print("Selected logging level: {}".format(args.loglevel))
    print("Selected output format: {}".format(args.format))

    # Create the directory if it does not exist
    os.makedirs(args.path, exist_ok=True)

    nodes = get_nodes(args.token, args.file)
    logging.debug("All nodes as JSON: {}".format(nodes))

    nodes_to_export = find_values("exportSettings", nodes)
    logging.debug("Nodes to export: {}".format(nodes_to_export))

    for node in nodes_to_export:
        image_url = get_img_link(args.token, args.file, node[0], args.format)
        if image_url == None:
            logging.warning("Download link for image not found {}".format(image_name))
            continue
        image_name = node[1]
        logging.info("Downloading image {}".format(image_name))
        get_img(image_url, args.path, image_name, args.format)
