#!/bin/bash
echo '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  selector:
    matchLabels:
      run: prometheus
  replicas: 2
  template:
    metadata:
      labels:
        run: prometheus
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus
          ports:
            - containerPort: 9090
''' > ./argocd/prometheus/prometheus-deployment.yaml

echo '''
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  labels:
    run: prometheus
spec:
  ports:
    - name: prometheus
      port: 80
      targetPort: 9090
  type: LoadBalancer
  selector:
    run: prometheus
''' > ./argocd/prometheus/prometheus-svc.yaml

echo '''
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: prometheus
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: prometheus.hoanghd.fun
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: prometheus
                port:
                  number: 80
''' > ./argocd/prometheus/prometheus-ingress.yaml

# kubectl delete -f prometheus-deployment.yaml
# kubectl delete -f prometheus-svc.yaml
# kubectl delete -f prometheus-ingress.yaml
# kubectl apply -f prometheus-deployment.yaml
# kubectl apply -f prometheus-svc.yaml
# kubectl apply -f prometheus-ingress.yaml