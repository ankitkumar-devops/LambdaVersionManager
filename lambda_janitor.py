import boto3
from datetime import datetime, timedelta, timezone
import random
import logging
import  traceback

LOGGER = logging.getLogger('lambda_version_cleanup')
LOGGER.setLevel(logging.INFO)


lambda_client = boto3.client('lambda', region_name='us-east-1')


def list_functions():
    LOGGER.info('Listing all available functions')
    all_functions = []

    response = lambda_client.list_functions(MaxItems=20)

    while 'Functions' in response:
        all_functions.extend(response['Functions'])
        if 'NextMarker' in response:
            response = lambda_client.list_functions(MaxItems=20, Marker=response['NextMarker'])
        else:
            break

    return [function['FunctionArn'] for function in all_functions]


def list_versions(func_arn):
    LOGGER.info(f'Listing versions for function: {func_arn}')
    all_versions = []

    response = lambda_client.list_versions_by_function(FunctionName=func_arn, MaxItems=20)

    while 'Versions' in response:
        all_versions.extend(response['Versions'])
        if 'NextMarker' in response:
            response = lambda_client.list_versions_by_function(
                FunctionName=func_arn, MaxItems=20, Marker=response['NextMarker']
            )
        else:
            break

    return [version['Version'] for version in all_versions if version['Version'] != '$LATEST']


def list_aliased_versions(func_arn):
    LOGGER.info(f'Listing aliases for function: {func_arn}')
    all_aliases = []

    response = lambda_client.list_aliases(FunctionName=func_arn, MaxItems=20)

    while 'Aliases' in response:
        all_aliases.extend(response['Aliases'])
        if 'NextMarker' in response:
            response = lambda_client.list_aliases(FunctionName=func_arn, MaxItems=20, Marker=response['NextMarker'])
        else:
            break

    return [alias['FunctionVersion'] for alias in all_aliases]


def delete_version(func_arn, version):
    LOGGER.info(f'Deleting [{func_arn}] version [{version}]')
    lambda_client.delete_function(FunctionName=func_arn, Qualifier=version)


def get_version_creation_date(func_arn, version):
    version_details = lambda_client.get_function(FunctionName=func_arn, Qualifier=version)
    version_creation_date_str = version_details['Configuration']['LastModified']
    version_creation_date = datetime.strptime(version_creation_date_str, "%Y-%m-%dT%H:%M:%S.%f+0000")
    return version_creation_date

def clean_func(func_arn, n):
    LOGGER.info(f'Cleaning function: {func_arn}')
    aliased_versions = list_aliased_versions(func_arn)
    LOGGER.info(f'Found aliased versions:\n{aliased_versions}')

    versions = list_versions(func_arn)
    LOGGER.info(f'Found versions:\n{versions}')

    current_date = datetime.now(timezone.utc)

    # Sort versions based on creation date
    versions.sort(key=lambda v: get_version_creation_date(func_arn, v))

    # Keep the latest 5 versions
    versions_to_keep = versions[-n:]

    for version in versions:
        if version not in aliased_versions:
            version_details = lambda_client.get_function(FunctionName=func_arn, Qualifier=version)

            version_creation_date_str = version_details['Configuration']['LastModified']
            version_creation_date = datetime.strptime(version_creation_date_str, "%Y-%m-%dT%H:%M:%S.%f+0000")
            version_creation_date = version_creation_date.replace(tzinfo=timezone.utc)

            age_in_days = (current_date - version_creation_date).days

            if version in versions_to_keep or age_in_days <= 90:
                LOGGER.info(f'Keeping version [{version}] created {abs(age_in_days)} days ago.')
            else:
                LOGGER.info(f'Deleting version [{version}] created {age_in_days} days ago.')
                delete_version(func_arn, version)


def lambda_handler(event, context):
    try:
        n = event.get("last_version_no", 5)
        functions = []

        if not functions:
            functions = list_functions()
            
        clean_all_fun = list(functions)
        LOGGER.info(f'{len(clean_all_fun)} functions to clean:\n{clean_all_fun}')

        for func in clean_all_fun:
            clean_func(func, n)
            functions.remove(func)
        return {'statusCode': 200, 'body': 'Cleanup completed successfully!'}
    except Exception as e:
        LOGGER.error(f'Error during cleanup: {e}')
        traceback.print_exc()
        
