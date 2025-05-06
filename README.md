# 🚀 Deploying Your Full Stack App on AWS EKS

This guide walks you through configuring your EKS cluster and deploying all services, including your frontend (WebUI).

---

## ✅ 1. Get the `kubeconfig` for Your EKS Cluster

This command sets up your local `kubectl` to connect to the cluster named `surv-2`.

```bash
aws eks update-kubeconfig --name surv-2
```

* This pulls down your cluster’s kubeconfig.
* You must have the correct AWS credentials (`aws configure`) for the account that owns the cluster.

---

## 📦 2. Deploy Core Backend Services

You need to deploy **video-processor**, **index**, and **router** services to the cluster.

> 🗂 These should be defined in Kubernetes manifests (`.yaml` files) for deployments and services.

```bash
kubectl apply -f manifests/video-deploy.yaml
kubectl apply -f manifests/index-deploy.yaml
kubectl apply -f manifests/router-deploy.yaml
```

---

## 🔒 3. Check Security Groups

Ensure your EKS worker nodes' security group allows **inbound traffic** to necessary ports (usually 80/443 or custom app ports like 30002, 30003).

* Go to **EC2 > Security Groups** in AWS Console.
* Find the security group attached to the EKS nodes.
* Add an inbound rule like:

| Type       | Protocol | Port Range  | Source                       |
| ---------- | -------- | ----------- | ---------------------------- |
| Custom TCP | TCP      | 30000-32767 | 0.0.0.0/0 (or your IP range) |

> This is needed because EKS NodePorts expose services on high ports by default.

---

## 🌐 4. Get NodePort IPs

Use this command to get the **external IP** and **port** for your services:

```bash
kubectl get svc
```

Example output:

```
NAME               TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)           AGE
index-service      NodePort   10.0.1.34       <none>        30003:30003/TCP   2m
router-service     NodePort   10.0.1.56       <none>        30002:30002/TCP   2m
```

* Find the IP of any worker node (`kubectl get nodes -o wide`) and use it along with the exposed port.
* Example:

  * `http://<node-ip>:30002` → for `BASE_PROCESSING_URL`
  * `http://<node-ip>:30003` → for `BASE_INDEX_URL`

---

## 📝 5. Update `.env` File for WebUI

Update your WebUI `.env` file with correct URLs and AWS config:

```dotenv
VITE_AWS_ACCESS_KEY_ID=your-access-key
VITE_AWS_SECRET_ACCESS_KEY=your-secret-key
VITE_AWS_REGION=us-east-1
VITE_S3_BUCKET_NAME=surv-cloud-videos
VITE_BASE_PROCESSING_URL=http://<node-ip>:30002
VITE_BASE_INDEX_URL=http://<node-ip>:30003
```

Make sure there are **no spaces** around the `=` signs.

---

## 🛠 6. Build and Push WebUI Docker Image

Assuming you have a `Dockerfile` in the WebUI directory:

```bash
# Build the Docker image
docker build -t your-dockerhub-user/webui:latest .

# Log in to Docker Hub
docker login

# Push the image
docker push your-dockerhub-user/webui:latest
```

---

## 🚢 7. Deploy WebUI to EKS

Create a Kubernetes deployment and service for WebUI:

```bash
kubectl apply -f k8s/webui-deployment.yaml
kubectl apply -f k8s/webui-service.yaml
```

Make sure the service type is `NodePort` (or `LoadBalancer` if you’re using an ELB).

Now access your WebUI at:

```bash
http://<node-ip>:30001
```