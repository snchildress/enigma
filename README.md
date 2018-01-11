# Enigma

Enigma is an application for sharing sensitive data at Lucid. It will consist of features to address three use cases: sharing sensitive plain text data on an adhoc basis, securing a repository of shared sensitive data, and sharing sensitive documents on an adhoc basis.

## Getting Started

To get started, clone this repository, instatiate and activate a virtual environment, and install all requirements.

```
git clone https://github.com/lucidhq/enigma
virtualenv venv-enigma
source venv/bin/activate
pip install -r requirements.txt
```

To contribute, branch off of the `develop` branch as either `feature/name` or `bug/name` and submit a PR to `develop`

## Built With

Enigma is built off of [Python](https://python.org)'s [Django](https://djangoproject.com) framework using Google's [Material Design Components](https://material.io/components/web/) on the frontend and hosted in the cloud using AWS's [Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/).

## API Documentation

### Authorization

You must pass in the valid API key in the header as `{"Authorization": API_KEY}` to use the Enigma API

### Environments

Enigma has 2 environments that differ by the base URL:

- Production: `https://enigma.lucidhq.solutions/`
- Development: `https://enigma-dev.lucidhq.engineering/`

### `POST` Create a Secret

Endpoint: `secret/create`

Creates a new secret message and returns a one-time access URL to that secret. Use `\n` in the message string to insert a line break.

#### Parameters

| Parameter Name  | Data Type   |  Required 	|  Description 	                           |
|-----------------|-------------|---------------|------------------------------------------|
| message         | string      | yes        	| secret message to display to recipient   |
| success         | boolean     | no            | success status of request attempt        |
| message_url     | string      | no            | URL to access secret message once        |

#### Example Requests & Responses

##### Request Body

```
{
    "message": "u: username\np: password"
}
```

##### Sucessful Response Body

Status Code: 200
```
{
    "message_url": "https://enigma.lucidhq.solutions/secret/confirm/4a52e96d-6053-4fcb-9ed1-6c8ede1f9bdd",
    "success": true
}
```

##### Bad Request Response Body

Status Code: 400

```
{
    "message": "Request body missing the 'message' parameter",
    "success": false
}
```

##### Unauthorized Response Body

Status Code: 403
```
{
    "message": "Invalid API key",
    "success": false
}
```

##### Invalid Method Response Body

Status Code: 405
```
{
    "message": "Invalid method",
    "success": false
}
```

## Additional Documentation

This [proposal](https://docs.google.com/document/d/1Y6Auw5azimS5MpI1qPMfv5xGLXKD-K_g-iwgkZx5NRk/) describes the various features and considerations for building Enigma.
