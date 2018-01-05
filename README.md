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
Enigma is built off of [Python](https://python.org)'s [Django](https://djangoproject.com) framework using Google's [Material Design Lite](https://getmdl.io/) on the frontend and hosted in the cloud using AWS's [Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/).

## Additional Documentation
This [proposal](https://docs.google.com/document/d/1Y6Auw5azimS5MpI1qPMfv5xGLXKD-K_g-iwgkZx5NRk/) describes the various features and considerations for building Enigma.