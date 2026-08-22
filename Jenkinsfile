pipeline {
    agent any
    
    options {
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'production'],
            description: 'Select environment'
        )
        choice(
            name: 'ACTION',
            choices: [
                'CHECK_STATUS',
                'START_INFRASTRUCTURE',
                'STOP_INFRASTRUCTURE',
                'DEPLOY_LOCAL',
                'DEPLOY_TO_AWS',
                'RUN_TESTS',
                'FULL_CYCLE'
            ],
            description: 'Select action to perform'
        )
    }
    
    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        AWS_ACCOUNT_ID = credentials('aws-account-id')
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        DOCKER_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com"
        TERRAFORM_DIR = "infrastructure/terraform/aws"
    }
    
    stages {
        stage('Initialize') {
            steps {
                script {
                    echo "🚀 CallSync Jenkins Pipeline"
                    echo "Environment: ${params.ENVIRONMENT}"
                    echo "Action: ${params.ACTION}"
                    echo "Timestamp: ${new Date()}"
                    
                    // Verify AWS credentials
                    sh '''
                        echo "Verifying AWS credentials..."
                        aws sts get-caller-identity
                        if [ $? -eq 0 ]; then
                            echo "✓ AWS credentials verified"
                        else
                            echo "✗ AWS credentials invalid"
                            exit 1
                        fi
                    '''
                }
            }
        }
        
        stage('Check Status') {
            when {
                expression { 
                    params.ACTION == 'CHECK_STATUS' || 
                    params.ACTION == 'FULL_CYCLE'
                }
            }
            steps {
                script {
                    echo "📊 Checking infrastructure status..."
                    sh '''
                        chmod +x ./INFRASTRUCTURE_STATUS.sh
                        ./INFRASTRUCTURE_STATUS.sh
                    '''
                }
            }
        }
        
        stage('Start Infrastructure') {
            when {
                expression { 
                    params.ACTION == 'START_INFRASTRUCTURE' || 
                    params.ACTION == 'FULL_CYCLE'
                }
            }
            steps {
                script {
                    echo "🚀 Starting AWS infrastructure for ${params.ENVIRONMENT}..."
                    sh '''
                        chmod +x ./START_INFRASTRUCTURE.sh
                        ./START_INFRASTRUCTURE.sh <<< "yes"
                        
                        if [ $? -eq 0 ]; then
                            echo "✓ Infrastructure started successfully"
                        else
                            echo "✗ Infrastructure startup failed"
                            exit 1
                        fi
                    '''
                }
            }
        }
        
        stage('Stop Infrastructure') {
            when {
                expression { params.ACTION == 'STOP_INFRASTRUCTURE' }
            }
            steps {
                script {
                    echo "⏹️  Stopping AWS infrastructure for ${params.ENVIRONMENT}..."
                    sh '''
                        chmod +x ./STOP_INFRASTRUCTURE.sh
                        ./STOP_INFRASTRUCTURE.sh <<< "destroy everything"
                        
                        if [ $? -eq 0 ]; then
                            echo "✓ Infrastructure stopped successfully"
                        else
                            echo "✗ Infrastructure stop failed"
                            exit 1
                        fi
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            when {
                expression { 
                    params.ACTION == 'RUN_TESTS' || 
                    params.ACTION == 'FULL_CYCLE'
                }
            }
            parallel {
                stage('Backend Tests') {
                    steps {
                        script {
                            echo "🧪 Running backend tests..."
                            sh '''
                                cd backend
                                python -m pytest tests/test_integration.py -v --tb=short
                            '''
                        }
                    }
                }
                
                stage('Frontend Build') {
                    steps {
                        script {
                            echo "🏗️  Building frontend..."
                            sh '''
                                cd frontend
                                npm install
                                npm run build
                            '''
                        }
                    }
                }
                
                stage('Mobile Build') {
                    steps {
                        script {
                            echo "📱 Validating mobile app..."
                            sh '''
                                cd mobile
                                npm install
                                npx tsc --noEmit
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Deploy Local') {
            when {
                expression { 
                    params.ACTION == 'DEPLOY_LOCAL' || 
                    params.ACTION == 'FULL_CYCLE'
                }
            }
            steps {
                script {
                    echo "🚀 Deploying locally..."
                    sh '''
                        chmod +x ./DEPLOY_AUTOMATED.sh
                        ./DEPLOY_AUTOMATED.sh
                        
                        if [ $? -eq 0 ]; then
                            echo "✓ Local deployment successful"
                        else
                            echo "✗ Local deployment failed"
                            exit 1
                        fi
                    '''
                }
            }
        }
        
        stage('Deploy to AWS') {
            when {
                expression { params.ACTION == 'DEPLOY_TO_AWS' }
            }
            steps {
                script {
                    echo "☁️  Deploying to AWS ${params.ENVIRONMENT}..."
                    sh '''
                        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
                        
                        echo "Building Docker images..."
                        docker build -t callsync-api:${BUILD_NUMBER} ./backend
                        docker tag callsync-api:${BUILD_NUMBER} ${DOCKER_REGISTRY}/callsync-api:${BUILD_NUMBER}
                        docker tag callsync-api:${BUILD_NUMBER} ${DOCKER_REGISTRY}/callsync-api:latest
                        
                        echo "Pushing to ECR..."
                        aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${DOCKER_REGISTRY}
                        docker push ${DOCKER_REGISTRY}/callsync-api:${BUILD_NUMBER}
                        docker push ${DOCKER_REGISTRY}/callsync-api:latest
                        
                        echo "Updating ECS service..."
                        aws ecs update-service \
                            --cluster callsync-${ENVIRONMENT} \
                            --service callsync-api \
                            --force-new-deployment
                        
                        echo "✓ Deployment to AWS ${ENVIRONMENT} initiated"
                    '''
                }
            }
        }
        
        stage('Health Check') {
            when {
                expression { 
                    params.ACTION != 'STOP_INFRASTRUCTURE'
                }
            }
            steps {
                script {
                    echo "🏥 Running health checks..."
                    sh '''
                        chmod +x ./INFRASTRUCTURE_STATUS.sh
                        ./INFRASTRUCTURE_STATUS.sh
                        
                        # Extract and test API endpoint
                        ALB_DNS=$(terraform -chdir=${TERRAFORM_DIR} output -raw alb_dns_name 2>/dev/null || echo "N/A")
                        
                        if [ "$ALB_DNS" != "N/A" ]; then
                            echo "Testing API health at: http://$ALB_DNS/health"
                            
                            for i in {1..30}; do
                                HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$ALB_DNS/health 2>/dev/null || echo "000")
                                if [ "$HTTP_CODE" = "200" ]; then
                                    echo "✓ API health check passed"
                                    exit 0
                                fi
                                echo "Attempt $i: HTTP $HTTP_CODE (waiting...)"
                                sleep 10
                            done
                            echo "✗ API health check failed"
                            exit 1
                        else
                            echo "⚠️  Could not determine ALB DNS"
                        fi
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "📋 Pipeline Summary"
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Action: ${params.ACTION}"
                echo "Status: ${currentBuild.result}"
            }
        }
        
        success {
            script {
                echo "✅ Pipeline completed successfully!"
                
                // Save build artifacts
                archiveArtifacts artifacts: '**/infrastructure-running.txt', allowEmptyArchive: true
                
                // Send notification (if configured)
                // emailext(
                //     subject: "✅ CallSync Pipeline Success - ${params.ACTION}",
                //     body: "Pipeline ${params.ACTION} on ${params.ENVIRONMENT} completed successfully",
                //     to: "team@example.com"
                // )
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed!"
                
                // Send notification (if configured)
                // emailext(
                //     subject: "❌ CallSync Pipeline Failed - ${params.ACTION}",
                //     body: "Pipeline ${params.ACTION} on ${params.ENVIRONMENT} failed. Check logs.",
                //     to: "team@example.com"
                // )
            }
        }
    }
}
