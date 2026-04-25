# Local Kubernetes: kind, minikube, k3d, colima

Running K8s on your laptop is for learning, manifest iteration, and running the same CI cluster locally. It is not a substitute for a non-production managed cluster before you touch production.

## Which local cluster

| Tool | Runtime | Start time | Strength | Weakness |
|---|---|---|---|---|
| kind | Docker-in-Docker | ~60 s | Official, multi-node, used heavily in K8s CI. | No built-in dashboard; LoadBalancer needs extras. |
| k3d | Docker + k3s | ~15 s | Very fast, tiny footprint, great DX. | k3s differences (Traefik default, containerd-specific bits). |
| minikube | VM or Docker | ~90 s | Mature, rich addons (dashboard, ingress, registry). | Heavier, slower, VM baggage on macOS/Windows. |
| colima (macOS/Linux) | Lima VM + containerd | ~45 s | Docker-compatible daemon for Mac; k8s toggle. | macOS/Linux only; one cluster. |
| Docker Desktop Kubernetes | Docker Desktop VM | included | Zero install if you already use Docker Desktop. | Single node, slower to reset, licensing. |

Rule: pick one and stop. Switching local clusters daily wastes more time than it saves.

## kind quickstart

```bash
# Install (brew / choco / apt)
brew install kind kubectl

# Create a multi-node cluster with mapped ports for Ingress
cat > kind.yaml <<'YAML'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: dev
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
    extraPortMappings:
      - { containerPort: 80,  hostPort: 80,  protocol: TCP }
      - { containerPort: 443, hostPort: 443, protocol: TCP }
  - role: worker
  - role: worker
YAML

kind create cluster --config kind.yaml
kubectl cluster-info --context kind-dev

# Install ingress-nginx tuned for kind
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod --selector=app.kubernetes.io/component=controller \
  --timeout=180s

# Load an image you built locally, without a registry
docker build -t myapi:dev .
kind load docker-image myapi:dev --name dev
```

Delete the cluster cleanly:

```bash
kind delete cluster --name dev
```

## k3d quickstart

```bash
brew install k3d

k3d cluster create dev \
  --servers 1 --agents 2 \
  --port "80:80@loadbalancer" --port "443:443@loadbalancer" \
  --registry-create k3d-registry:0.0.0.0:5001

# Push to local registry
docker tag myapi:dev k3d-registry:5001/myapi:dev
docker push k3d-registry:5001/myapi:dev
```

k3d starts very quickly and ships with Traefik by default; disable if you prefer ingress-nginx:

```bash
k3d cluster create dev --k3s-arg "--disable=traefik@server:0"
```

## minikube quickstart

```bash
brew install minikube
minikube start --driver=docker --cpus=4 --memory=8g --nodes=2
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable registry

# Point your shell at minikube's Docker daemon to avoid a push
eval $(minikube docker-env)
docker build -t myapi:dev .
```

To reach a Service:

```bash
minikube service api -n default   # opens a URL
# or
minikube tunnel                    # exposes LoadBalancer Services on localhost
```

## Local container registry

A local registry avoids rebuilding images into every cluster.

```bash
# Plain registry
docker run -d --name registry --restart=always -p 5001:5000 registry:2

# kind: hook up the registry
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: local-registry-hosting
  namespace: kube-public
data:
  localRegistryHosting.v1: |
    host: "localhost:5001"
    help: "https://kind.sigs.k8s.io/docs/user/local-registry/"
EOF

docker network connect kind registry
docker tag myapi:dev localhost:5001/myapi:dev
docker push localhost:5001/myapi:dev
```

In your manifests reference `localhost:5001/myapi:dev`.

## Fast inner loop: Skaffold

Skaffold watches your source, rebuilds the image, pushes to the local registry (or loads into kind), and re-applies manifests.

```yaml
# skaffold.yaml
apiVersion: skaffold/v4beta11
kind: Config
build:
  artifacts:
    - image: myapi
      docker: { dockerfile: Dockerfile }
  local:
    push: false                                # rely on kind load
deploy:
  kubectl:
    manifests: [k8s/*.yaml]
portForward:
  - resourceType: service
    resourceName: api
    port: 80
    localPort: 8080
```

```bash
skaffold dev                 # watch + rebuild + redeploy
skaffold run --tail          # one-shot deploy with logs
```

## Fast inner loop: Tilt

Tilt is an alternative with a browser UI showing each resource's status and logs.

```python
# Tiltfile
docker_build('myapi', '.', dockerfile='Dockerfile')
k8s_yaml(['k8s/deploy.yaml', 'k8s/svc.yaml'])
k8s_resource('api', port_forwards='8080:3000')
```

```bash
tilt up
```

Use Tilt for multi-service repos where the UI pays off; Skaffold is lighter for a single service.

## port-forward patterns

```bash
# Service
kubectl port-forward svc/api 8080:80

# Deployment (picks one Pod)
kubectl port-forward deploy/api 8080:3000

# Multiple ports at once
kubectl port-forward svc/postgres 5432:5432 9187:9187

# Bind to all interfaces (useful in a VM)
kubectl port-forward --address 0.0.0.0 svc/api 8080:80
```

port-forward is for debugging, not production traffic. Prefer `kubectl proxy` or telepresence for more complex local-to-cluster debugging.

## Housekeeping

- Delete clusters when idle: `kind delete cluster`, `k3d cluster delete`, `minikube delete`. Idle VMs burn RAM.
- Prune images: `docker system prune -af` once a week.
- Keep local K8s version within one minor of production. Drift causes confusing manifest behaviour.
- Use one `KUBECONFIG` per project (direnv) so `kubectl get pods` in the wrong terminal cannot hit production.

## Common local-only gotchas

- `type: LoadBalancer` Services stay `<pending>` unless you enable MetalLB (kind), use `minikube tunnel`, or rely on k3d's built-in LB.
- Volumes on Docker Desktop have different permissions than Linux; test with the same filesystem you will deploy against.
- Pulling huge images over slow Wi-Fi kills the feedback loop. Use the local registry.
- Resource limits from production will crash laptop-sized runs; consider a `dev` overlay (Kustomize) that scales requests down.
