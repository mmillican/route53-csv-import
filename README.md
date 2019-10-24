# Route 53 CSV Import

Import DNS records from a CSV file into AWS Route 53.

## File Format

The CSV file should be in the format:

```txt
Name,Type,Data
```

## Running the import

Requires boto3

```
$ pip install boto3
```

Currently, this tool assumes you have `default` credentials specified in `~/.aws/credentials` and will use those for the import.

```
$ python r53import.py <file-name> <hosted-zone-id> "<comment-for-batch">
```