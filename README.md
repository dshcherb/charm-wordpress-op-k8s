# Deployment Preparation

In order to use the charm, you need to place the Operator Framework modules under lib. Use `Makefile` to do that:

```
make build
```

# MicroK8s Setup

```
sudo snap install juju --classic
sudo snap install microk8s --classic
microk8s.enable dns dashboard registry storage
juju bootstrap microk8s
juju deploy ./charm-wordpress-op-k8s
```

# Known Issues

* K8s charms do not get an `install` event fired (`start` event is fired instead), thus the mechanism of auto-creating symlinks in the framework does not work. See https://bugs.launchpad.net/juju/+bug/1854635. This should be fixed after https://github.com/canonical/operator/pull/63 is merged.
