Message formats categorized by message types:

While uploading a new file:
1. Request nameserver for blocks into which the file has to be divided and where to store that partition -> 
{
    "msg_type": 1, 
    "uuid": `uuid`, 
    "filename": `filename`, 
    "file_size": size
}
2. Reply from nameserver to client with blocks and where to upload file -> 
{
    "msg_type": "2", 
    "uuid": `uuid`, 
    "filename": `filename`, 
    "file_size": `size`, 
    "partitions": [
        {
            "block_num": "#", 
            "primary_storage_loc": "<aws/gcp/azure>",
            "secondary_storage_loc": "<aws/gcp/azure>",
            "block_start": "#", 
            "block_end": "#",
            "partition_uuid": "<partition_uuid>"
        },
         .
         .
         .
        ]
}
3. Upload file message to fileserver -> 
{
    "msg_type": "3",
    "uuid": "uuid",
    "file": [
        {
            "primary_storage_loc": "<aws/gcp/azure>",
            "secondary_storage_loc": "<aws/gcp/azure>","file_content":"<stringyfied_file>", 
            "file_path": "<uuid>/<filename>/<block_num>/<partition_uuid>"
        },
        .
        .
        .
        ]
}
4. Acknowledgement from fileserver of the file upload -> 
{
    "msg_type": "4",
    "uuid": "uuid", 
    "ACK": "ACK/NACK"
}
5. Updating an existing file ->
{
    "msg_type": "5", 
    "uuid": `uuid`, 
    "filename": `filename`, 
    "file_size": `size`, 
    "old_partitions": [
        {
            "block_num": "#", 
            "primary_storage_loc": "<aws/gcp/azure>",
            "secondary_storage_loc": "<aws/gcp/azure>",
            "block_start": "#", 
            "block_end": "#",
            "partition_uuid": "<partition_uuid>"
        },
         .
         .
         .
    ]
    "partitions": [
        {
            "block_num": "#", 
            "primary_storage_loc": "<aws/gcp/azure>",
            "secondary_storage_loc": "<aws/gcp/azure>",
            "block_start": "#", 
            "block_end": "#",
            "partition_uuid": "<partition_uuid>"
        },
         .
         .
         .
    ]
}

While downloading file:
1. Request nameserver for file -> 
{
    "msg_type": "5", 
    "uuid": `uuid`, 
    "filename": `filename`
}
2. Reply from nameserver to client with details of partitions of the file -> 
{
    "msg_type": "6", 
    "uuid": `uuid`, 
    "filename": `filename`, 
    "have_access": "Y/N", 
    "partitions": [
        {
            "block_num": "#", 
            "primary_storage_loc": "<aws/gcp/azure>",
            "secondary_storage_loc": "<aws/gcp/azure>", 
            "block_start": "#", 
            "block_end": "#", 
            "file_path": "<uuid>/<filename>/<block_num>/<partition_uuid>"
        }, 
        .
        .
        .
    ] //Not sent when no access to file exists
}
<!-- 3. Request to fileserver for file -> 
{
    "msg_type":"7", 
    "uuid":`uuid`, 
    "file_metadata": [{"file_path": "<uuid>/<filename>_<block_num>", "storage_loc": "aws/azure/gcp"}, ...]
}
4. Response of File data from all clouds to be sent to client:
{
    "msg_type": "8",
    "uuid": "uuid",
    "file_data": [{"file_path": "<uuid>/<filename>_<block_num>", "file": "<stringyfied_file>"}, ...]
} -->

When deleting a file:
1. Request from client to nameserver to delete file:
{
    "msg_type":"9",
    "uuid":"uuid",
    "filename":"filename"
}
2. Response from nameserver to the request to delete file:
{
    "msg_type":"10",
    "uuid":"uuid",
    "HAVE_ACCESS": "Y/N",
    "partitions": [
        {
            "block_num": "#", 
            "primary_storage_loc": "<aws/gcp/azure>",
            "secondary_storage_loc": "<aws/gcp/azure>",
            "block_start": "#", 
            "block_end": "#",
            "file_path": "<uuid>/<filename>/<block_num>/<partition_uuid>"
        },
         .
         .
         .
        ] //Not sent when no access to file exists
}
<!-- 3. Request to delete file partitions to fileserver:
{
    "msg_type": "11",
    "uuid": "uuid",
    "file": [{"storage_loc":"<aws/gcp/azure>", "file_path": "<uuid>/<filename>/<block_num>/<partition_uuid>"}, ...]
}
4. Response from fileserver:
{
    "msg_type": "12",
    "uuid": "uuid",
    "ACK": "ACK/NACK"
} -->



FileTable:
{
    "<client_uuid>": [
        {
            "<filename>": [
                {
                    "partition_uuid": <partition_uuid>,
                    "block_num": <block_num>,
                    "block_start": <start_byte_of_partition_in_file>,
                    "block_end": <end_byte_of_partition_in_file>,
                    "primary_storage_loc": <aws/gcp/azure>,
                    "secondary_storage_loc": <aws/gcp/azure>
                },
                .
                .
                .
            ]
        }
    ],
    .
    .
    .
}


Client_conns:
{
    "<addr>": {
        "socket": <client_socket>,
        "client_uuid": <client_uuid>
    },

}