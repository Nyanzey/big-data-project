# Kubernetes EKS Surveillance Project

This project demonstrates a Kubernetes-based video surveillance system running on an AWS EKS cluster. The application includes a user interface exposed via a NodePort service, enabling access from a public IP.

## Prerequisites

Before getting started, ensure you have the following installed and configured:

- AWS CLI
- `eksctl`
- `kubectl`
- AWS account with permissions to create EKS clusters and EC2 instances
- Git

---

## Steps to Deploy the Project

### 1. Create an AWS EKS Cluster (Auto Mode)

To simplify the process, we use `eksctl` to automatically provision the EKS cluster and its worker nodes.

Run the following command:

```bash
eksctl create cluster --name surveillance-cluster --region us-east-1 --nodes 2 --managed
````

* Replace `surveillance-cluster` with a name of your choice.
* Adjust `--region` and `--nodes` as needed.
* This process takes around 10–15 minutes and will configure your `kubectl` context automatically.

> **Note:** Make sure your AWS CLI is configured using `aws configure` before running the above command.

---

### 2. Clone This Repository

Clone the project to your local machine:

```bash
git clone https://github.com/Nyanzey/big-data-project.git
cd big-data-project
```

> Replace the URL with the actual repository URL if different.

---

### 3. Deploy the Kubernetes Manifests

Apply the provided manifests to the cluster:

```bash
kubectl apply -f manifests/
```

This will deploy the application components including the NodePort UI service.

---

### 4. Identify the Node Running the UI Service

Get the name of the UI service pod:

```bash
kubectl get pods -o wide
```

Find the pod for the UI (it may have "ui" in its name), then note the `NODE` column — this is the EC2 instance hosting the pod.

Next, find the public IP of that instance:

```bash
kubectl get nodes -o wide
```

The `EXTERNAL-IP` column corresponds to the public IP of each node.

---

### 5. Modify the EC2 Instance's Inbound Rules

Go to the AWS EC2 Console:

1. Find the instance corresponding to the node running the UI.
2. Click on the instance and navigate to its **Security Group**.
3. Edit **Inbound Rules**:

   * Add a new rule:

     * **Type**: Custom TCP
     * **Port Range**: `30001`
     * **Source**: `0.0.0.0/0` (or restrict as needed)

This allows access to the NodePort from the internet.

---

### 6. Access the UI in Your Browser

Once the security rules are updated, open your browser and go to:

```
http://<public-ip>:30001
```

Replace `<public-ip>` with the public IP of the EC2 instance running the UI pod.

You should now see the application's user interface.

---

## Troubleshooting

* If the UI is not accessible, ensure:

  * The pod is running and assigned to a node.
  * The NodePort (`30001`) is correct and matches the service definition.
  * The security group allows traffic on port 30001.
  * The cluster has healthy nodes and no pending pods.

---
