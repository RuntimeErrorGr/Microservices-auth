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
   6. Enable istio addons: minikube addons enable istio-provisioner minikube addons enable istio
   7. Enable minikube tunnel: sudo minikube tunnel

   ### Persistent postgres for keycloak:

   This guy explains how to setup keycloak with postgres local + how to add tls to it.
   https://www.youtube.com/watch?v=SJrvqQF6qA0&t=1343s

## Important notes:

### (21.11.2024)

1. Keycloak has persistent storage, so you can restart the pod without losing data. But this storage is local, on my laptop :)).
   **If you want to use it, you need to follow the tutorial above.**
   ```
   sudo -u postgres psql postgres
   ```
2. There are some secrets that you need to create in the cluster in order to access the app via istio gateway.
   **You can find them in the mytls and mytls-2 folders.**
3. In order to access the app via istio gateway you can type in your browser: http://posd-app.com (for the webapp) and http://posd-app-keycloak.com (for keycloak dashboard).
4. Generate a JWT token with keycloak:

   ```
   curl -k -X POST -d "client_id=Istio" -d "username=book-user" -d "password=123" -d "grant_type=password" "https://posd-app-keycloak.com/realms/Istio/protocol/openid-connect/token"
   ```

   The response should look like this (but with another token):

   ```
   {"access_token":"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ5bExMVzA5VVVUbHR2MVVzbkZpWG5OYnpLMHhTVGFzaHc5MFNSWkNGU1JJIn0.eyJleHAiOjE3MzIxNDIwNjQsImlhdCI6MTczMjE0MTc2NCwianRpIjoiZjEwMmYxMTAtYWRjZi00ZmIwLWJkYjUtZjcxNzI2OWY4MmIwIiwiaXNzIjoiaHR0cHM6Ly9wb3NkLWFwcC1rZXljbG9hay5jb20vcmVhbG1zL0lzdGlvIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImMxMGQ0NDI2LTVmMWMtNDA1Yi1iYmU0LTM3Njk2YjY2MzJhYiIsInR5cCI6IkJlYXJlciIsImF6cCI6IklzdGlvIiwic2Vzc2lvbl9zdGF0ZSI6IjhmYjIwZjZjLWNiNzAtNGU5Yi1iYmYzLTExNjc3ZmY2ZTZhNiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsInVzZXIiLCJkZWZhdWx0LXJvbGVzLWlzdGlvIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIiwic2lkIjoiOGZiMjBmNmMtY2I3MC00ZTliLWJiZjMtMTE2NzdmZjZlNmE2IiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJCb29rIFVzZXIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJib29rLXVzZXIiLCJnaXZlbl9uYW1lIjoiQm9vayIsImZhbWlseV9uYW1lIjoiVXNlciIsImVtYWlsIjoiYm9vay11c2VyQGV4bWFwbGUuY29tIn0.bWzB9Ixr2oZYu4IhNmT5A-yj-VbSsqhWEOG6g1KWbi1dDYhgZJ5W8Ks_ioUyb_ABuRFitPMoWCh9wrgoNuzAv8H3_oKFjk3aljsHrj9c0BsI7BzGGEMKA4lUVHLXJbM73BHhdYvw1hQ0XDmTfdE6hZYgY_0LqC92eqP9gKZ4dAGHvMwJZT2B1I5rIeDtjcwSSz7g5GOaL4hTah_s8ys_lEXoKDy9gU8hD1fjCfMSPMP2q3J96tVi2RY06BKGkx7iV1fC8DCWT-xtw3NwPmVPEv99UGidZB3UQ4rvLLRoINZ8oNkO2BF21w-XRiHJmCq6EHYihMdY2zTVPbxrIPgMqg","expires_in":300,"refresh_expires_in":1800,"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3YTJlOThlYy01MzRlLTRlY2MtYTkzYi1lYTYzNGFlMTBmOTMifQ.eyJleHAiOjE3MzIxNDM1NjQsImlhdCI6MTczMjE0MTc2NCwianRpIjoiMmExM2MyOGQtODFjOS00NzI3LTkzMDUtZTQyNDBhZWQ5NzU4IiwiaXNzIjoiaHR0cHM6Ly9wb3NkLWFwcC1rZXljbG9hay5jb20vcmVhbG1zL0lzdGlvIiwiYXVkIjoiaHR0cHM6Ly9wb3NkLWFwcC1rZXljbG9hay5jb20vcmVhbG1zL0lzdGlvIiwic3ViIjoiYzEwZDQ0MjYtNWYxYy00MDViLWJiZTQtMzc2OTZiNjYzMmFiIiwidHlwIjoiUmVmcmVzaCIsImF6cCI6IklzdGlvIiwic2Vzc2lvbl9zdGF0ZSI6IjhmYjIwZjZjLWNiNzAtNGU5Yi1iYmYzLTExNjc3ZmY2ZTZhNiIsInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsInNpZCI6IjhmYjIwZjZjLWNiNzAtNGU5Yi1iYmYzLTExNjc3ZmY2ZTZhNiJ9.7VfceCzi2itN6FwiED4-MlvXTf0N88_7xwvncWs4tgE","token_type":"Bearer","not-before-policy":0,"session_state":"8fb20f6c-cb70-4e9b-bbf3-11677ff6e6a6","scope":"email profile"}
   ```

5. Use the access_token to access the webapp:

   ```
   curl -k
   ```

## How to deploy the whole thing:

1. Go through the prerequisites setup.
2. Just _kubeclt apply -f_ all .yaml files you find (would be nice to have a script for this).
