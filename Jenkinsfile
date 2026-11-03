pipeline {
    agent any

    environment {
        IMAGE_NAME     = 'system-health-dashboard'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = "health-api-${env.BUILD_NUMBER}"
        TEST_PORT      = '5050'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m pytest -v
                '''
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t $IMAGE_NAME:latest .'
            }
        }

        stage('Tag') {
            steps {
                sh '''
                    docker tag $IMAGE_NAME:latest $IMAGE_NAME:$IMAGE_TAG
                    docker images $IMAGE_NAME
                '''
            }
        }

        stage('Health check') {
            steps {
                sh '''
                    docker run -d --name $CONTAINER_NAME -p $TEST_PORT:5000 -e APP_ENV=ci $IMAGE_NAME:$IMAGE_TAG
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                        if curl -fsS http://host.docker.internal:$TEST_PORT/health; then
                            echo ""
                            echo "Health check passed"
                            exit 0
                        fi
                        echo "Waiting for app... attempt $i"
                        sleep 2
                    done
                    echo "Health check failed"
                    docker logs $CONTAINER_NAME
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rm -f $CONTAINER_NAME || true'
        }
    }
}
