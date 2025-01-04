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
   Create them in deafult and istio-system namespaces.
3. In order to access the app via istio gateway you can type in your browser: http://posd-app.com (for the webapp) and http://posd-app-keycloak.com (for keycloak dashboard).
4. Generate a JWT token with keycloak:

   ```
   curl -k -X POST -d "client_id=Istio" -d "username=book-user" -d "password=123" -d "grant_type=password" "https://posd-app-keycloak.com/realms/Istio/protocol/openid-connect/token"
   ```

   The response should look like this (but with another token):

   ```
   {"access_token":"<token>","expires_in":300,"refresh_expires_in":1800,"refresh_token":"****","token_type":"Bearer","not-before-policy":0,"session_state":"8fb20f6c-cb70-4e9b-bbf3-11677ff6e6a6","scope":"email profile"}
   ```

5. Test if istio authorization works:

   ```
   curl -k -H -X "POST" "Authorization: Bearer \*insert token here\*\*" http://posd-app.com/teapot
   ```

   The response should be:

   ```
   I'm a teapot from the POSD project app
   ```

### (22.11.2024)

We have 4 microservices until now up and running in kubernetes:

1. webserver
2. keycloak
3. books_information
4. books_information_db

How to test books_information:

1. Exec into webserver (the books_information client is accesible only inside cluster #TODO: restrict it only to webserver).

```
kubectl exec -it *webserver_pod_name* -- /bin/bash
```

2. Make a request

```
curl -s http://books-information-service:8080/books | python3 -m json.tool
```

Response should be:

```
[
    {
        "bookId": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "Fiction",
        "publicationDate": "1925-04-10",
        "isbn": "9780743273565",
        "description": "A novel set in the Jazz Age."
    },
    {
        "bookId": 2,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Fiction",
        "publicationDate": "1960-07-11",
        "isbn": "9780060935467",
        "description": "A tale of racial injustice and childhood innocence."
    }
]
```

### (29.12.2024)

1. Keycloak persistent storage is in kubernetes now.
2. We have a minimal frontend with login page, dashboard, book page and a generic layout.
   ![app3](https://github.com/user-attachments/assets/9f5864bb-0d44-40b5-8b5f-b54b49fd84e7)
   ![app1](https://github.com/user-attachments/assets/d53e6f6f-b043-46dc-b6c6-e3857127ad43)
   ![app2](https://github.com/user-attachments/assets/8753ade2-47c4-4f08-b519-93dfa90d6be1)
3. We have 3 roles: guest, user and verified-user and view operation on books and reviews. The rest of CRUD operations are TBD.

## How to deploy the whole thing:

1. Go through the prerequisites setup.
2. Just _kubeclt apply -f_ all .yaml files you find (would be nice to have a script for this).
3. Have fun.
