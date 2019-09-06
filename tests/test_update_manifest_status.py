import pytest
import boto3
from moto import mock_dynamodb2, mock_events
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lambdas.update_manifest_status_handler import ManifestHandler

manifest_table_name = "dev-CurationManifestFilesTable"
manifest_index_name = "dev-BatchId-TableName-index"


@mock_dynamodb2
def create_mock_table():
    ddb = boto3.client('dynamodb', region_name='us-east-1')
    ddb.create_table(AttributeDefinitions=[{
            'AttributeName': 'ManifestId',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'BatchId',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'TableName',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'FileStatus',
            'AttributeType': 'S'
        }],
        TableName=manifest_table_name,
        KeySchema=[
            {
                'AttributeName': 'ManifestId',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'BatchId',
                'KeyType': 'RANGE'
            }
        ],
        GlobalSecondaryIndexes=[{
            'IndexName': manifest_index_name,
            'KeySchema': [
                {
                    'AttributeName': 'BatchId',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'TableName',
                    'KeyType': 'RANGE'
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL',
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 15,
                'WriteCapacityUnits': 20
            }
        }],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 10
        },
    )

@mock_dynamodb2
def test_update_manifest_status_raises_exception():
    create_mock_table()
    with pytest.raises(Exception):
        ddb = boto3.client('dynamodb', region_name='us-east-1')
        test_event = dict()
        test_event["batchId"] = str(int(time.time()))
        test_event["tablename"] = "alert"
        update_manifest_obj = ManifestHandler()
        update_manifest_obj.update_manifest_status(test_event, None)


@mock_dynamodb2
def test_update_manifest_status():
    create_mock_table()
    ddb = boto3.client('dynamodb', region_name='us-east-1')
    os.environ["DDB_MANIFEST_TABLE_ARN"] = "arn:aws:dynamodb:us-east-1::table/dev-CurationManifestFilesTable"
    os.environ["DDB_MANIFEST_FILES_INDEX_NAME"] = "dev-BatchId-TableName-index"
    test_event = dict()
    test_event["batchId"] = str(int(time.time()))
    test_event["tablename"] = "alert"
    update_manifest_obj = ManifestHandler()
    update_manifest_obj.update_manifest_status(test_event, None)
    assert True


@mock_dynamodb2
def test_update_manifest_status_with_item():
    create_mock_table()
    ddb = boto3.client('dynamodb', region_name='us-east-1')
    ddb_res = boto3.resource('dynamodb', region_name='us-east-1')
    batch_id = '17476592384'
    table = ddb_res.Table(manifest_table_name)
    table.put_item(
           Item={
               'ManifestId': 'dev-BatchId-TableName-index',
               'BatchId': batch_id,
               'TableName': manifest_table_name,
               'FileStatus': 'open',
            }
        )
    os.environ["DDB_MANIFEST_TABLE_ARN"] = "arn:aws:dynamodb:us-east-1::table/dev-CurationManifestFilesTable"
    os.environ["DDB_MANIFEST_FILES_INDEX_NAME"] = manifest_index_name
    test_event = dict()
    test_event["batchId"] = batch_id
    test_event["tablename"] = manifest_table_name
    update_manifest_obj = ManifestHandler()
    update_manifest_obj.update_manifest(test_event, None)
    assert True


@mock_events
def test_update_manifest():
    with pytest.raises(Exception):
        # test_event = dict()
        # test_event["batchId"] = str(int(time.time()))
        # test_event["tablename"] = "alert"
        update_manifest_obj = ManifestHandler()
        assert update_manifest_obj.update_manifest_status(None, None) is None