// Continuous Delivery pipeline for the System Health Dashboard API.
//   develop / main : test, build once, deploy to staging automatically, smoke test, verify monitoring
//   main only      : wait for a human approval, deploy the SAME image to production, smoke test
//   any failure    : roll the touched environment(s) back to the last known good tag

// True when the build is for one of the given branches. Works in a multibranch job (BRANCH_NAME)
// and in a plain "Pipeline script from SCM" job (GIT_BRANCH, for example origin/main).
def onBranch(List names) {
    def current = (env.BRANCH_NAME ?: env.GIT_BRANCH ?: '').replaceFirst(/^origin\//, '')
    return names.contains(current)
}

pipeline {
    agent any

    options {
        // Two builds deploying at the same time would fight over the same containers
        disableConcurrentBuilds()
    }

    triggers {
        // Nobody has to click Build Now: new commits are picked up every couple of minutes
        pollSCM('H/2 * * * *')
    }

    environment {
        IMAGE_NAME     = 'system-health'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        IMAGE          = "system-health:${env.BUILD_NUMBER}"
        CONTAINER_NAME = "health-api-${env.BUILD_NUMBER}"
        TEST_PORT      = '5050'
        // Jenkins itself runs in a container, so the apps (published on the Docker host) are
        // reached through host.docker.internal rather than localhost
        DEPLOY_HOST    = 'host.docker.internal'
        PROMETHEUS_URL = 'http://host.docker.internal:9090'
        // Last known good tag per environment, written only after that environment's smoke test passes
        STATE_DIR      = "${env.JENKINS_HOME}/system-health-state"
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

        stage('Build and tag') {
            steps {
                // Built exactly once. Staging and production both run this tag.
                sh '''
                    docker build -t $IMAGE .
                    docker tag $IMAGE $IMAGE_NAME:latest
                    docker images $IMAGE_NAME
                '''
            }
        }

        stage('Health check') {
            steps {
                sh '''
                    docker run -d --name $CONTAINER_NAME -p $TEST_PORT:5000 -e ENVIRONMENT=ci $IMAGE
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                        if curl -fsS http://$DEPLOY_HOST:$TEST_PORT/health; then
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

        stage('Deploy to Staging') {
            when { expression { onBranch(['develop', 'main']) } }
            steps {
                sh '''
                    docker compose version
                    docker network create sre-monitoring || true
                '''
                // Set before deploying so a failure part-way through still triggers the rollback
                script { env.STAGING_DEPLOYED = 'true' }
                sh 'docker compose -p staging -f docker-compose.staging.yml up -d'
            }
        }

        stage('Smoke test (staging)') {
            when { expression { onBranch(['develop', 'main']) } }
            steps {
                sh './scripts/smoke_test.sh http://$DEPLOY_HOST:5001'
                sh 'mkdir -p $STATE_DIR && echo $BUILD_NUMBER > $STATE_DIR/last_good_staging'
            }
        }

        stage('Verify monitoring') {
            when { expression { onBranch(['develop', 'main']) } }
            steps {
                // A new container needs up to one scrape interval before Prometheus reports it UP
                retry(4) {
                    sleep 10
                    sh '''
                        curl -fsS --data-urlencode 'query=up{job="system-health",environment="staging"}' \
                            $PROMETHEUS_URL/api/v1/query | tee prometheus-up.json
                        echo ""
                        grep -Eq '"value":\\[[0-9.]+,"1"\\]' prometheus-up.json
                    '''
                }
            }
        }

        stage('Approval') {
            when { expression { onBranch(['main']) } }
            steps {
                // Continuous Delivery: a person decides when production gets this build.
                // An approval timeout aborts the build, which does not trigger the rollback.
                timeout(time: 30, unit: 'MINUTES') {
                    script {
                        def approver = input(
                            message: "Deploy ${env.IMAGE} to production?",
                            ok: 'Deploy',
                            submitterParameter: 'APPROVER'
                        )
                        echo "Production release approved by ${approver}"
                    }
                }
            }
        }

        stage('Deploy to Production') {
            when { expression { onBranch(['main']) } }
            steps {
                script { env.PROD_DEPLOYED = 'true' }
                // No docker build here: Compose starts the image that already passed staging
                sh 'docker compose -p production -f docker-compose.production.yml up -d'
            }
        }

        stage('Smoke test (production)') {
            when { expression { onBranch(['main']) } }
            steps {
                sh './scripts/smoke_test.sh http://$DEPLOY_HOST:5002'
                sh 'echo $BUILD_NUMBER > $STATE_DIR/last_good_production'
            }
        }
    }

    post {
        always {
            sh 'docker rm -f $CONTAINER_NAME || true'
        }
        failure {
            // Only environments this build actually touched are rolled back
            script {
                if (env.STAGING_DEPLOYED == 'true') {
                    sh './scripts/rollback.sh staging'
                }
                if (env.PROD_DEPLOYED == 'true') {
                    sh './scripts/rollback.sh production'
                }
            }
        }
    }
}
