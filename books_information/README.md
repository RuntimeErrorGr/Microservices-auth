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