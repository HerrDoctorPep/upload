# Readme

## Project description

Little git repository to test file upload.

Objectives:
- Prove small Docker image with Python
- Deploy code to Azure web app
- Connect docker container as local storage when deployed

## Learnings

### Docker image

- I let go of Conda in favour of `venv` to get a much smaller docker image(too much weight in conda)
- Started from `ubuntu:latest` image with a few additional `apt-get install` things.
- Needed to install `python3`, `python3-venv`, and `python3-pip` separately (first installing `software-properties-common` and `gpg-agent` to allow use of different repo
as mentioned [here](https://github.com/dbt-labs/dbt-core/issues/7352))
- Decided to roll back `openssl` to version 1.1.1 anticipating use of Azure AI (cf. speech2text error correspondence)

As long as I develop in the devcontainer, I don´t need to worry about a `venv`.
If I wantto develop locally, it is necessary to separate things.

At some point I want to make a requirements file for `apt-get` as well, like [here](https://www.monolune.com/articles/installing-apt-packages-from-a-requirements-file/); to improve maintainablity.

```bash
sed 's/#.*//' config/requirements.system | xargs sudo apt-get install
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

