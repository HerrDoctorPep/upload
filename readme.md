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
ssh-add ~/.ssh/github-ssh
```

### Deployment approach

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

Simple deployment based on standard image does not work in this case, because I need to install additional packages like `ffmpeg`.
Alternative is to use an [Azure container registry](https://portal.azure.com/#@microsoftvdlaan.onmicrosoft.com/resource/subscriptions/020d939e-2d58-4a61-8612-a9424b3ad869/resourceGroups/s2tapp/providers/Microsoft.ContainerRegistry/registries/s2tcontainer/overview) with a custom container.

- Webapp deployment allows to write a `docker-compose.yml` to customuze deployment.
- Secrets can be passed as environmnet variables in configuration.

### Local testing
Local testing of the app goes through building and running a container as defined in `Dockerfile` and `docker-compose.yml`.
```bash
docker build -t uploadpipeline .
docker compose up
```
Environment variables are picked up from the `.env` to ensure access to Azure blob storage. To open the test-app visit: `localhost:5000`.

### Uploading the image

```bash
az login
az acr login --name s2tcontainer
az acr list --resource-group s2tapp --output table

docker tag uploadpipeline s2tcontainer.azurecr.io/uploadpipeline
docker push s2tcontainer.azurecr.io/uploadpipeline
```

## Status and to do's

Now works when deployed as web app

### Bugs
- [ ] Write last line of summary correctly to file
- [ ] Handle longer podcasts smoothly in summarization (transcript length > max context)

### Feature requests 
- [ ] Make solution configurable via yaml (Az resources used, prompts, summary length)
- [ ] Upload via browsing and/or typing file location (in addition to drag-and-drop)
- [ ] Return path from overview of summaries to upload page
- [ ] Option to display summary in text window on 'summaries' page (as alternative to downloading the text file)

### Need version for interview-based podcasts
- [ ] Solve for context window overshoot of transcript
- [ ] Transcription solution for multiple voices
