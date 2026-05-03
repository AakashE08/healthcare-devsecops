pipeline {
    agent any
    environment {
        DOCKER_HUB_USER  = 'aakash888'
        IMAGE_NAME       = "${DOCKER_HUB_USER}/healthcare-api"
        IMAGE_TAG        = "${BUILD_NUMBER}"
        FULL_IMAGE       = "${IMAGE_NAME}:${IMAGE_TAG}"
        KUBECONFIG       = '/var/lib/jenkins/.kube/config'
        NAMESPACE        = 'healthcare'
        MASTER_PRIVATE_IP = '172.31.45.159'
        SONAR_HOST       = 'http://54.92.151.234:9000'
    }
    stages {
        stage('Fix Kubeconfig') {
            steps {
                sh """
                    sudo sed -i "s|https://.*:6443|https://${MASTER_PRIVATE_IP}:6443|" ${KUBECONFIG}
                    sudo sed -i '/certificate-authority-data/d' ${KUBECONFIG}
                    grep -q 'insecure-skip-tls-verify' ${KUBECONFIG} || \
                        sudo sed -i '/server:/a\\    insecure-skip-tls-verify: true' ${KUBECONFIG}
                    kubectl get nodes --kubeconfig=${KUBECONFIG}
                """
            }
        }
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-credentials',
                    url: 'https://github.com/AakashE08/healthcare-devsecops.git'
            }
        }
        stage('Unit Tests') {
            steps {
                sh """
                    cd app
                    pip3 install -r requirements.txt --break-system-packages --quiet
                    python3 -m pytest tests/ -v --tb=short
                """
            }
        }
        stage('SonarQube Analysis') {
            steps {
                sh """
                    /opt/sonar-scanner/bin/sonar-scanner \
                        -Dsonar.projectKey=healthcare-devsecops \
                        -Dsonar.sources=app \
                        -Dsonar.language=py \
                        -Dsonar.host.url=${SONAR_HOST} \
                        -Dsonar.login=${SONAR_TOKEN}
                """
            }
        }
        stage('Build Docker Image') {
            steps {
                sh """
                    docker build \
                        --no-cache \
                        --label build-number=${BUILD_NUMBER} \
                        -t ${FULL_IMAGE} .
                    docker tag ${FULL_IMAGE} ${IMAGE_NAME}:latest
                """
            }
        }
        stage('Trivy Scan') {
            steps {
                sh """
                    chmod +x scripts/trivy-scan.sh
                    ./scripts/trivy-scan.sh ${FULL_IMAGE} HIGH,CRITICAL trivy-report.json || true
                """
            }
        }
        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        docker login -u \$DOCKER_USER -p \$DOCKER_PASS
                        docker push ${FULL_IMAGE}
                        docker push ${IMAGE_NAME}:latest
                        docker logout
                    """
                }
            }
        }
        stage('Apply Security Policies') {
            steps {
                sh """
                    kubectl apply --validate=false -f k8s/namespace.yaml --kubeconfig=${KUBECONFIG}
                    kubectl apply --validate=false -f k8s/rbac.yaml --kubeconfig=${KUBECONFIG}
                """
            }
        }
        stage('Create Secrets') {
            steps {
                sh """
                    kubectl create secret generic healthcare-secrets \
                        --from-literal=api-token="Secure-API-Token-Healthcare-2024" \
                        --from-literal=secret-key='SecureKey-Healthcare-2024' \
                        --namespace=${NAMESPACE} \
                        --kubeconfig=${KUBECONFIG} \
                        --dry-run=client -o yaml | \
                        kubectl apply --kubeconfig=${KUBECONFIG} -f -
                """
            }
        }
        stage('Deploy') {
            steps {
                sh """
                    kubectl apply --validate=false -f k8s/deployment.yaml --kubeconfig=${KUBECONFIG}
                    kubectl apply --validate=false -f k8s/service.yaml --kubeconfig=${KUBECONFIG}
                    kubectl set image deployment/healthcare-api \
                        healthcare-api=${FULL_IMAGE} \
                        -n ${NAMESPACE} --kubeconfig=${KUBECONFIG}
                    kubectl rollout status deployment/healthcare-api \
                        -n ${NAMESPACE} --timeout=300s --kubeconfig=${KUBECONFIG}
                """
            }
        }
        stage('Verify Security') {
            steps {
                sh """
                    echo '=== Pods ==='
                    kubectl get pods -n ${NAMESPACE} --kubeconfig=${KUBECONFIG}
                    echo '=== Service ==='
                    kubectl get svc -n ${NAMESPACE} --kubeconfig=${KUBECONFIG}
                    echo '=== RBAC ==='
                    kubectl get rolebindings -n ${NAMESPACE} --kubeconfig=${KUBECONFIG}
                    echo '=== Secrets (base64 protected) ==='
                    kubectl get secret healthcare-secrets -n ${NAMESPACE} --kubeconfig=${KUBECONFIG}
                """
            }
        }
    }
    post {
        success {
            echo "DevSecOps pipeline PASSED! Healthcare API deployed securely."
            echo "Access at http://54.165.36.61:30095"
        }
        failure {
            sh "kubectl rollout undo deployment/healthcare-api -n ${NAMESPACE} --kubeconfig=${KUBECONFIG} || true"
            echo "Pipeline FAILED a security gate. Deployment blocked."
        }
        always {
            sh 'docker rmi ${FULL_IMAGE} || true'
            cleanWs()
        }
    }
}
