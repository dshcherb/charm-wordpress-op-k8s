# Deployment Preparation

In order to use the charm, you need to place the Operator Framework modules under lib. Use `Makefile` to do that:

```
make build
```

# MicroK8s Setup
sudo snap install juju --classic
sudo snap install microk8s --classic
microk8s.enable dns dashboard registry storage
juju bootstrap microk8s
juju deploy ./charm-wordpress-k8s
