pipeline {
    agent any

    environment {
        IMAGE_NAME = "kvr-brick-works-image"
        CONTAINER_NAME = "kvr-brick-works-container"
        APP_PORT = "5000"
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/nithish063/kvr-brick-works.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}")
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    // Stop and remove existing container if it exists
                    bat """
                    docker rm -f ${CONTAINER_NAME} || true
                    """

                    // Run the new container
                    bat """
                    docker run -d -p ${APP_PORT}:${APP_PORT} --name ${CONTAINER_NAME} ${IMAGE_NAME}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Application deployed successfully and running on port ${APP_PORT}."
        }
        failure {
            echo "Build or deployment failed. Please check the logs for details."
        }
    }
}
