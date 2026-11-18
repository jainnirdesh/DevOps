#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
export HOMEBREW_NO_AUTO_UPDATE=1
brew install colima docker docker-buildx docker-compose kubectl minikube
# Keep plugin discovery scoped to this user's standard Docker CLI plugin directory.
mkdir -p "$HOME/.docker/cli-plugins"
for plugin in buildx compose; do
    target="$(brew --prefix)/opt/docker-$plugin/bin/docker-$plugin"
    if [ ! -e "$target" ]; then
        target="$(brew --prefix)/opt/docker-$plugin/lib/docker/cli-plugins/docker-$plugin"
    fi
    destination="$HOME/.docker/cli-plugins/docker-$plugin"
    if [ ! -e "$destination" ] && [ -e "$target" ]; then
        ln -s "$target" "$destination"
    fi
done
colima start --profile lab2 --cpu 4 --memory 6 --disk 30 --vm-type vz --mount-type virtiofs
export DOCKER_CONTEXT=colima-lab2
docker version
docker buildx version
docker-compose version
