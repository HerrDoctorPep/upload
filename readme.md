# Readme

## Project description

Little git repository to test file upload.

Objectives:
- Prove small Docker image with Python
- Deploy code to Azure web app
- Connect docker container as local storage when deployed

## Learnings

### Development

- I let go of Conda in favour of `venv` to get a much smaller docker image(too much weight in conda)
- Started from Dockerś standard `python:3.10` image instead (as installing on top of `ubuntu:latest` led to too much issues to resolve)

With `devcontainer` even venv is not needed. Just spin up container with dependencies from the right `requirements.txt`

In the dev container start the app: 
```bash
gunicorn app:app
```


### Git

Added an ssh key following [this](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) in the secrets folder.

Make key available:
```bash
eval "$(ssh-agent -s)"
ssh-add config/github-ssh
```

### Deploying the app

I follow [this tutorial](https://learn.microsoft.com/en-us/azure/developer/python/tutorial-containerize-simple-web-app-for-app-service?tabs=web-app-flask)

With connection to Github, Azure makes its own container and ignores the `Dockerfile` 
- Environmennt variables for the webapp can be set through Azure portal: 
  - 'Configuration' tab of the webapp resource
    - 'Application settings' tab therein
- Mounting Azure storage as local drive through Azure portal as well:
  -  'Configuration' tab of the webapp resource
     -  'Path mappings' tab therein
-  Azure Active Directory used for access control
   -  Users are created via Azure Active Directory service
   -  Access control via IAM tab of the webapp resource

### Local testing
Local testing of the app goes through building and running a container as defined in `Dockerfile` and `docker-compose.yml`.
```bash
docker build --tag uploadapp .
docker compose up
```
Environment variables are picked up from the `.env` to ensure access to Azure blob storage. To open the test-app visit: `localhost:5000`.

## Status and to do's

Upload to blob works in test container (develop branch). Still to be deployed to production. 

### Need smoother user experience in the app 
- [ ] Status updates while the process runs
- [ ] Download links for transcript and summary

### Need version for interviews
- [ ] Solve for context window overshoot of transcript
- [ ] Transcription solution for multiple voices
