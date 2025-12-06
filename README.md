# Kubernetes EKS Surveillance Project

This project implements a distributed video surveillance system deployed on an **AWS EKS** (Elastic Kubernetes Service) cluster.
The system includes three main modules—**WebUI**, **Video Preprocessing**, and **Inverted Index**—all running as Kubernetes workloads.
The WebUI is exposed via a **NodePort service**, making the interface accessible from a node’s public IP.

### Créditos

- Bruno Fernandez Gutierrez (bruno.fernandez@ucsp.edu.pe)
- Joaquin Pino Zavala (joaquin.pino@ucsp.edu.pe)
- Fredy Quispe Neira (fredy.quispe@ucsp.edu.pe)
- Marco Guillen Davila (marco.guillen@ucsp.edu.pe)

---

## 1. Prerequisites

Before beginning, ensure you have the following tools installed and configured:

* **AWS CLI** (properly configured with `aws configure`)
* **eksctl**
* **kubectl**
* **Git**
* An AWS account with permissions to create EKS clusters and EC2 instances

---

## 2. Project Architecture

### 2.1 Modules Overview

The project is composed of three modules:

1. **WebUI**

   * Built with **React + Vite**
   * Allows users to upload videos and search for detected objects

2. **Video Preprocessing**

   * Implemented in **Python** using **YOLO** for object detection
   * Exposes an API using **Flask**
   * Processes videos and extracts metadata such as detected objects, timestamps, and frame numbers

3. **Inverted Index Builder**

   * Implemented in **Python**
   * Stores the inverted index in **SQLite**
   * Exposes a Flask API to serve search queries
   * Maps each object to the videos and timestamps where it appears

---

### 2.2 Deployment Environment

All modules are deployed on an **AWS EKS Kubernetes cluster**, ensuring:

* Scalable video processing (multiple worker nodes)
* Containerized communication via well-defined APIs
* Separation of responsibilities between modules

Technologies used across the stack:

| Module           | Technologies          |
| ---------------- | --------------------- |
| WebUI            | React + Vite          |
| Video Processing | Python, YOLO, Flask   |
| Inverted Index   | Python, SQLite, Flask |

---

### 2.3 Workflow

Communication between modules occurs through:

* Flask REST APIs (`video-processing` and `inverted-index`)
* HTTP requests from the WebUI (React + Vite)

**Workflow Steps**

1. The user uploads a video through the WebUI.
2. The WebUI uploads the video to an S3 bucket.
3. The WebUI sends a processing request to the Video Processing module.
4. The Video Processing module downloads the video from S3.
5. The video is processed and annotated using [YOLO](https://github.com/ultralytics/ultralytics).
6. Metadata is sent to the Inverted Index module.
7. The Inverted Index updates the index with the new metadata.
8. The user performs an object search in the WebUI.
9. The WebUI sends a query to the Inverted Index module.
10. The Inverted Index responds with videos and timestamps where the object appears.
11. The WebUI displays results to the user.

---

## 3. Deployment Guide

### Step 1 — Create an AWS EKS Cluster

Using `eksctl`, create a managed EKS cluster:

```bash
eksctl create cluster --name surveillance-cluster --region us-east-1 --nodes 2 --managed
```

You may adjust:

* Cluster name (`--name`)
* Region (`--region`)
* Node count (`--nodes`)

> This process takes ~10–15 minutes and automatically updates your `kubectl` context.

---

### Step 2 — Clone the Repository

```bash
git clone https://github.com/Nyanzey/big-data-project.git
cd big-data-project
```

---

### Step 3 — Deploy Kubernetes Manifests

Apply all manifests located in the `manifests/` directory:

```bash
kubectl apply -f manifests/
```

This deploys all modules, including the NodePort service for the WebUI.

---

### Step 4 — Identify the Node Hosting the UI Pod

List all pods and their assigned nodes:

```bash
kubectl get pods -o wide
```

Find the pod containing `"ui"` in its name and note the `NODE` value.

Obtain the public IP of that node:

```bash
kubectl get nodes -o wide
```

Use the value in the `EXTERNAL-IP` column.

---

### Step 5 — Update EC2 Inbound Rules

To allow browser access to the WebUI via NodePort:

1. Open the AWS EC2 Console.
2. Select the EC2 instance corresponding to the UI pod's node.
3. Open its **Security Group**.
4. Edit **Inbound Rules**:

   * Type: **Custom TCP**
   * Port: `30001`
   * Source: `0.0.0.0/0` (or restrict as needed)

---

### Step 6 — Access the WebUI

Navigate to:

```
http://<public-ip>:30001
```

Replace `<public-ip>` with the public IP address of the node hosting the UI pod.

You should now see the surveillance system interface.

---

## 4. Troubleshooting

If the UI is not accessible:

* Ensure the UI pod is running and correctly scheduled to a node.
* Verify the NodePort matches `30001` or the value in your service manifest.
* Check that EC2 security groups allow inbound traffic on the NodePort.
* Confirm that cluster nodes are healthy and that no pods are stuck in `Pending`.
