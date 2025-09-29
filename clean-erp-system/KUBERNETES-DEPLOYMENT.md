# Kubernetes Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Cluster Setup](#cluster-setup)
4. [Application Deployment](#application-deployment)
5. [Service Configuration](#service-configuration)
6. [Ingress Setup](#ingress-setup)
7. [Monitoring & Logging](#monitoring--logging)
8. [Scaling & High Availability](#scaling--high-availability)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)

## Overview

This guide covers deploying the complete ERP system on Kubernetes clusters. Kubernetes provides orchestration, scaling, and management capabilities for containerized applications.

## Prerequisites

### 1. Kubernetes Cluster
- **Local**: Minikube, Kind, or Docker Desktop
- **Cloud**: EKS, GKE, AKS, or self-managed
- **Version**: 1.20+

### 2. Tools Required
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install docker (if building images locally)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

## Cluster Setup

### 1. Local Development (Minikube)
```bash
# Install minikube
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube
sudo mv minikube /usr/local/bin/

# Start minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Cloud Cluster (EKS)
```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create cluster
eksctl create cluster --name erp-cluster --region us-west-2 --nodegroup-name workers --node-type t3.medium --nodes 3 --nodes-min 1 --nodes-max 5
```

### 3. Verify Cluster
```bash
# Check cluster status
kubectl cluster-info

# Check nodes
kubectl get nodes

# Check namespaces
kubectl get namespaces
```

## Application Deployment

### 1. Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: erp-system
  labels:
    name: erp-system
```

### 2. ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: erp-config
  namespace: erp-system
data:
  DATABASE_URL: "postgresql://erp_user:erp_password@postgres:5432/erp_system"
  REDIS_URL: "redis://redis:6379/0"
  FLASK_ENV: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
```

### 3. Secrets
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: erp-secrets
  namespace: erp-system
type: Opaque
data:
  POSTGRES_PASSWORD: <base64-encoded-password>
  SECRET_KEY: <base64-encoded-secret-key>
  REDIS_PASSWORD: <base64-encoded-redis-password>
```

### 4. PostgreSQL Deployment
```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: erp-system
  labels:
    app: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        env:
        - name: POSTGRES_DB
          value: erp_system
        - name: POSTGRES_USER
          value: erp_user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: erp-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - erp_user
            - -d
            - erp_system
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - erp_user
            - -d
            - erp_system
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: erp-system
  labels:
    app: postgres
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
    protocol: TCP
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: erp-system
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: gp2
```

### 5. Redis Deployment
```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: erp-system
  labels:
    app: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:6-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: erp-system
  labels:
    app: redis
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
    protocol: TCP
  type: ClusterIP
```

### 6. Backend Deployment
```yaml
# k8s/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: erp-system
  labels:
    app: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: erp-backend:latest
        envFrom:
        - configMapRef:
            name: erp-config
        - secretRef:
            name: erp-secrets
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: app-logs
          mountPath: /app/logs
      volumes:
      - name: app-logs
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: erp-system
  labels:
    app: backend
spec:
  selector:
    app: backend
  ports:
  - port: 5000
    targetPort: 5000
    protocol: TCP
  type: ClusterIP
```

### 7. Frontend Deployment
```yaml
# k8s/frontend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: erp-system
  labels:
    app: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: erp-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: erp-system
  labels:
    app: frontend
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
  type: ClusterIP
```

## Service Configuration

### 1. Load Balancer Service
```yaml
# k8s/loadbalancer.yaml
apiVersion: v1
kind: Service
metadata:
  name: erp-loadbalancer
  namespace: erp-system
  labels:
    app: erp-system
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
    name: http
  - port: 443
    targetPort: 443
    protocol: TCP
    name: https
  selector:
    app: frontend
```

### 2. NodePort Service
```yaml
# k8s/nodeport.yaml
apiVersion: v1
kind: Service
metadata:
  name: erp-nodeport
  namespace: erp-system
  labels:
    app: erp-system
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
    protocol: TCP
    name: http
  selector:
    app: frontend
```

## Ingress Setup

### 1. Nginx Ingress Controller
```bash
# Install nginx ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.0/deploy/static/provider/cloud/deploy.yaml

# Wait for controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### 2. Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: erp-ingress
  namespace: erp-system
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - erp.yourdomain.com
    secretName: erp-tls
  rules:
  - host: erp.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 5000
```

### 3. SSL Certificate (Cert-Manager)
```bash
# Install cert-manager
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.5.3/cert-manager.yaml

# Create cluster issuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## Monitoring & Logging

### 1. Prometheus Setup
```bash
# Install Prometheus using Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin
```

### 2. Application Monitoring
```yaml
# k8s/monitoring.yaml
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: erp-backend-monitor
  namespace: erp-system
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: 5000
    path: /metrics
    interval: 30s
```

### 3. Logging with ELK Stack
```yaml
# k8s/logging.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch
  namespace: logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: elasticsearch:7.14.0
        env:
        - name: discovery.type
          value: single-node
        ports:
        - containerPort: 9200
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
  namespace: logging
spec:
  selector:
    app: elasticsearch
  ports:
  - port: 9200
    targetPort: 9200
```

## Scaling & High Availability

### 1. Horizontal Pod Autoscaler
```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: erp-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Pod Disruption Budget
```yaml
# k8s/pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: backend-pdb
  namespace: erp-system
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: backend
```

### 3. Network Policies
```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: erp-network-policy
  namespace: erp-system
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 5000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

## Security

### 1. RBAC Configuration
```yaml
# k8s/rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: erp-service-account
  namespace: erp-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: erp-role
  namespace: erp-system
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: erp-role-binding
  namespace: erp-system
subjects:
- kind: ServiceAccount
  name: erp-service-account
  namespace: erp-system
roleRef:
  kind: Role
  name: erp-role
  apiGroup: rbac.authorization.k8s.io
```

### 2. Security Context
```yaml
# k8s/security-context.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-secure
  namespace: erp-system
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: backend
        image: erp-backend:latest
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: tmp
        emptyDir: {}
      - name: logs
        emptyDir: {}
```

## Troubleshooting

### 1. Common Issues
```bash
# Check pod status
kubectl get pods -n erp-system

# Check pod logs
kubectl logs -f <pod-name> -n erp-system

# Check service endpoints
kubectl get endpoints -n erp-system

# Check ingress status
kubectl get ingress -n erp-system
```

### 2. Debug Commands
```bash
# Describe pod
kubectl describe pod <pod-name> -n erp-system

# Check events
kubectl get events -n erp-system --sort-by=.metadata.creationTimestamp

# Port forward for debugging
kubectl port-forward svc/backend 5000:5000 -n erp-system

# Execute commands in pod
kubectl exec -it <pod-name> -n erp-system -- /bin/bash
```

### 3. Performance Issues
```bash
# Check resource usage
kubectl top pods -n erp-system
kubectl top nodes

# Check HPA status
kubectl get hpa -n erp-system

# Check pod disruption budget
kubectl get pdb -n erp-system
```

## Deployment Scripts

### 1. Deploy Script
```bash
#!/bin/bash
# deploy.sh

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy database
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n erp-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n erp-system --timeout=300s

# Deploy application
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml

# Wait for application to be ready
kubectl wait --for=condition=ready pod -l app=backend -n erp-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n erp-system --timeout=300s

# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Deploy monitoring
kubectl apply -f k8s/monitoring.yaml

echo "Deployment completed successfully!"
```

### 2. Cleanup Script
```bash
#!/bin/bash
# cleanup.sh

# Delete ingress
kubectl delete -f k8s/ingress.yaml

# Delete application
kubectl delete -f k8s/backend.yaml
kubectl delete -f k8s/frontend.yaml

# Delete database
kubectl delete -f k8s/postgres.yaml
kubectl delete -f k8s/redis.yaml

# Delete configurations
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/secrets.yaml

# Delete namespace
kubectl delete -f k8s/namespace.yaml

echo "Cleanup completed successfully!"
```

## Conclusion

This Kubernetes deployment guide provides comprehensive instructions for deploying the ERP system on Kubernetes clusters. The guide covers everything from basic setup to advanced features like monitoring, scaling, and security.

For additional support, refer to the troubleshooting section or contact the development team.

