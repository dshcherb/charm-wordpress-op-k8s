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
juju create-storage-pool operator-storage kubernetes storage-class=microk8s-hostpath
juju deploy ./charm-wordpress-op-k8s
```

# Bundle and Config Example


`bundle.yaml`:

```
bundle: kubernetes
applications:
  wordpress:
    charm: ./
    # source: ./
    scale: 2
    options:
      container_config: include-file://container_config.yaml
```

`container_config.yaml`:

```
FOO: 1
BAR: 2
```

`juju deploy ./bundle.yaml`


The specified container config will be present in environment variables in both operator and workload pods:

```
juju run --unit wordpress/0 'env | grep -P "FOO|BAR"'
BAR=2
FOO=1

juju run --unit wordpress/1 'env | grep -P "FOO|BAR"'
BAR=2
FOO=1
```

```
microk8s.kubectl get po -n testmodel
NAME                  READY   STATUS    RESTARTS   AGE
wordpress-645df7c8b6-brjrf   1/1     Running   0          6m20s
wordpress-645df7c8b6-mwc5m   1/1     Running   0          6m20s
wordpress-operator-0         1/1     Running   0          6m27s
```

```
microk8s.kubectl exec -n testmodel -it wp-645df7c8b6-brjrf -- /bin/bash

root@wp-645df7c8b6-brjrf:/var/www/html# env | grep -P 'FOO|BAR'
FOO=1
BAR=2
```

# Known Issues

* K8s charms do not get an `install` event fired (`start` event is fired instead), thus the mechanism of auto-creating symlinks in the framework does not work. See https://bugs.launchpad.net/juju/+bug/1854635. This should be fixed after https://github.com/canonical/operator/pull/63 is merged;
* The 'db' relation is not implemented yet.
