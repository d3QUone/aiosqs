# aiosqs

[![pypi](https://img.shields.io/pypi/v/aiosqs.svg)](https://pypi.org/project/aiosqs/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aiosqs)

### About package

Python asynchronous and lightweight SQS client. The goal of this library is to provide fast and optimal access to SQS 
for Python projects, e.g. when you need a high-load queue consumer or high-load queue producer written in Python.

Supports Python versions 3.8, 3.9, 3.10, 3.11, 3.12.

Supported and tested Amazon-like SQS providers: Amazon, VK Cloud.


### Why aiosqs?

Main problem of `botocore` and `aiobotocore` is huge memory and CPU consumption.
Also `aiobotocore` itself is a transition of `botocore` to async interface without any optimizations.

Related issues:
- https://github.com/boto/boto3/issues/1670
- https://github.com/aio-libs/aiobotocore/issues/940
- https://github.com/aio-libs/aiobotocore/issues/970


### Installation

```shell
pip install aiosqs
```


### Usage

Create a client:
```python
from aiosqs import SQSClient

client = SQSClient(
    aws_access_key_id="access_key_id",
    aws_secret_access_key="secret_access_key",
    region_name="us-west-2",
    host="sqs.us-west-2.amazonaws.com",
)
```

Receive the queue url by queue name:
```python
response = await client.get_queue_url(queue_name=queue_name)
queue_url = response["QueueUrl"]
```

Send a message to the queue:
```python
response = await client.send_message(
    queue_url=queue_url,
    message_body=json.dumps({"demo": 1, "key": "value"}),
    delay_seconds=0,
)
print(response)
```

Receive a message from the queue:
```python
response = await client.receive_message(
    queue_url=queue_url,
    max_number_of_messages=1,
    visibility_timeout=30,
)
if response:
    print(response)
    receipt_handle = response[0]["ReceiptHandle"]
```

Delete the message from the queue:
```python
await client.delete_message(
    queue_url=queue_url,
    receipt_handle=receipt_handle,
)
```

Close the client at the end:
```python
await client.close()
```

Another option is to use `SQSClient` as an async context manager. No need to call `close` manually in this case. Example:
```python
from aiosqs import SQSClient

async with SQSClient(
    aws_access_key_id="access_key_id",
    aws_secret_access_key="secret_access_key",
    region_name="us-west-2",
    host="sqs.us-west-2.amazonaws.com",
) as client:
    response = await client.get_queue_url(queue_name="dev_orders")
    queue_url = response["QueueUrl"]
    print(queue_url)
```
