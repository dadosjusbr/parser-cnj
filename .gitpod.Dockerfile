FROM gitpod/workspace-full

USER gitpod

RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends ca-certificates libreoffice