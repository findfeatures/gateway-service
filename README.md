# Gateway Service

The gateway service is the main API service for the backend and public facing api.

The GS is split into two:
- private: api for the web-app
- public: requires api token for public users

# Installation

(To install a pyenv virtualenv)
```bash
pyenv virtualenv -p python3.6 3.6.8 gateway-service
```

Install the requirements into your virtualenv
```bash
pip install -e ".[dev]"
```

Run Unit Test
```bash
REDIS_URL=redis://127.0.0.1:6379/0 Make test
```

To run the service
```bash
Make run
```