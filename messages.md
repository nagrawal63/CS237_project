Message formats categorized by message types:

1. request nameserver for blocks into which the file has to be divided and where to store that partition -> {"msg_type": 1, "uuid": `uuid`, "filename": `filename`, "file_size": size}
2. Reply from nameserver to client with blocks and where to upload file -> {"client_uuid": `uuid`, "filename": `filename`, "file_size": `size`, "partitions": [{"block_num": "#", "storage_loc": "aws/gcp/azure", "block_start": "#", "block_end": "#"}, ...]}
3.