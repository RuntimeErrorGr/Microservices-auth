# POSD-project README

## Prerequisites setup

1. Make sure you have QEMU/KVM virtualization support enabled and working.
2. Ensure that you have kubectl installed.

   ### Install minikube.

   1. curl -LO https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2
   2. sudo install docker-machine-driver-kvm2 /usr/local/bin/
   3. Start the cluster: minikube start --driver=kvm2
   4. Check if you have access to it: kubectl get po -A
   5. Open cluster dashboard: minikube dashboard

   ### Persistent postgres for keycloak:

   This guy explains how to setup keycloak with postgres local + how to add tls to it.
   https://www.youtube.com/watch?v=SJrvqQF6qA0&t=1343s

## Important notes (21.11.2024):

1. Keycloak has persistent storage, so you can restart the pod without losing data. But this storage is local, on my laptop.
   **If you want to use it, you need to follow the tutorial above.**
2. There are some secrets that you need to create in the cluster in order to access the app via istio gateway.
   **You can find them in the mytls and mytls-2 folders.**
3. In order to access the app via istio gateway you can type in your browser: http://posd-app.com (for the webapp) and http://posd-keycloak.com (for keycloak dashboard).

## How to deploy the whole thing:

1. Just make sure you have miniube running.
2. Go through the prerequisites setup.
3. Just _kubeclt apply -f_ all .yaml files you find (would be nice to have a script for this).
