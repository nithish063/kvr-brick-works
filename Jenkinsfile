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
                bat "docker build -t %IMAGE_NAME% --no-cache ."
            }
        }

        stage('Stop Existing Container') {
            steps {
                bat '''
                docker ps -a -q -f name=%CONTAINER_NAME% > container_id.txt
                set /p CONTAINER_ID=<container_id.txt
                if not "%CONTAINER_ID%"=="" (
                    docker rm -f %CONTAINER_NAME%
                ) else (
                    echo No existing container to remove.
                )
                del container_id.txt
                '''
            }
        }

        stage('Run Docker Container') {
            steps {
                bat "docker run -d -p %APP_PORT%:%APP_PORT% --name %CONTAINER_NAME% %IMAGE_NAME%"
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful! App running on port ${APP_PORT}."
        }
        failure {
            echo "❌ Build or deployment failed. Check logs."
        }
    }
}
