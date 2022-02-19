#!/bin/bash

# User inputs
DEPLOY_ADDRESS=
DEPLOY_TENANT=
DEPLOY_USER=
DEPLOY_PASSWORD=

# Global Variables
WORK_DIR=$(pwd)
APPLICATION_NAME=
APPLICATION_ID=
IS_FRONTEND=
IS_SUBSCRIBED=0
RELEASE_URL=""
MICROSERVICE_NAME="ewon-flexy-integration"
FRONTEND_APP_NAME="ewon-flexy-integration-app"
MICROSERVICE_LATEST_RELEASE_URL="https://api.github.com/repos/SoftwareAG/cumulocity-flexy-integration/releases/latest"
FRONTEND_LATEST_RELEASE_URL="https://api.github.com/repos/SoftwareAG/cumulocity-flexy-integration-ui/releases/latest"

DEPLOY_FRONTEND=1
DEPLOY_MICROSERVICE=1
HELP=1

#TAG_NAME="latest"

execute () {
	set -e
	installJqCommand
	readInput $@
	cd $WORK_DIR
	if [ "$HELP" == "0" ]
	then
		printHelp
		exit
	fi

	if [ "$DEPLOY_MICROSERVICE" == "0" ]
	then
		echo "[INFO] Start microservice deployment"
		IS_FRONTEND=0
		APPLICATION_NAME="$MICROSERVICE_NAME"
		setDefaults
		deploy
		echo "[INFO] End microservice deployment"
		echo
	fi
	if [ "$DEPLOY_FRONTEND" == "0" ]
	then
		echo "[INFO] Start frontend deployment"
		IS_FRONTEND=1
		APPLICATION_NAME="$FRONTEND_APP_NAME"
		setDefaults
		deploy
		echo "[INFO] End front deployment"
		echo
	fi
	exit 0
}

readInput () {
	echo "[INFO] Read input"
	while [[ $# -gt 0 ]]
	do
	key="$1"
	case $key in
		deployfe)
		DEPLOY_FRONTEND=0
		shift
		;;	
		deployms)
		DEPLOY_MICROSERVICE=0
		shift
		;;
		subscribe)
		SUBSCRIBE=0
		shift
		;;
		help | --help)
		HELP=0
		shift
		;;
		-dir | --directory)
		WORK_DIR=$2
		shift
		shift
		;;
		-n | --name)
		IMAGE_NAME=$2
		shift
		shift
		;;
		-t | --tag)
		TAG_NAME=$2
		shift
		shift
		;;
		url | --baseurl)
		DEPLOY_ADDRESS=$2
		shift
		shift
		;;
		-u | --user)
		DEPLOY_USER=$2
		shift
		shift
		;;
		-p | --password)
		DEPLOY_PASSWORD=$2
		shift
		shift
		;;
		-te | --tenant)
		DEPLOY_TENANT=$2
		shift
		shift
		;;
		-a | --application)
		APPLICATION_NAME=$2
		shift
		shift
		;;
		-id | --applicationId)
		APPLICATION_ID=$2
		shift
		shift
		;;
		-rel | --releaseUrl)
		RELEASE_URL=$2
		shift
		shift
		;;
		*)
		shift
		;;
	esac
	done
}

setDefaults () {
	IS_SUBSCRIBED=0
	IMAGE_NAME="$APPLICATION_NAME"
	ZIP_NAME="$IMAGE_NAME.zip"
	if [ "x$APPLICATION_NAME" == "x" ]
	then 
		APPLICATION_NAME=$IMAGE_NAME
	fi	
}

setReleaseUrl () {
	if [ "$IS_FRONTEND" == "0" ]
	then 
		RELEASE_URL=$(curl -s $MICROSERVICE_LATEST_RELEASE_URL | grep "browser_download_url.*zip" | cut -d : -f 2,3 | tr -d \")
	else RELEASE_URL=$(curl -s $FRONTEND_LATEST_RELEASE_URL | grep "browser_download_url.*zip" | cut -d : -f 2,3 | tr -d \")
	fi
}

printHelp () {
	echo
	echo "Following functions are available. You can specify them in single execution:"
	echo "	pack - prepares deployable zip file. Requires following stucture:"
	echo "		/docker/Dockerfile"
	echo "		/docker/* - all files within the directory will be included in the docker build"
	echo "		/cumulocity.json "
	echo "	deploy - deploys application to specified address"
	echo "	subscribe - subscribes tenant to specified microservice application"
	echo "	help | --help - prints help"
	echo 
	echo "Following options are available:"
	echo "	-dir | --directory 		# Working directory. Default value'$(pwd)' "
	echo "	-n   | --name 	 		# Docker image name"
	echo "	-t   | --tag			# Docker tag. Default value 'latest'"
	echo "	-d   | --deploy			# Address of the platform the microservice will be uploaded to"	
	echo "	-u   | --user			# Username used for authentication to the platform"
	echo "	-p   | --password 		# Password used for authentication to the platform"
	echo "	-te  | --tenant			# Tenant used"
	echo "	-a   | --application 	# Name upon which the application will be registered on the platform. Default value from --name parameter"
	echo "	-id  | --applicationId	# Application used for subscription purposes. Required only for solemn subscribe execution"
}

deploy () {
	setReleaseUrl
	verifyDeployPrerequisits
	downloadReleaseFromGit
	FILE=$WORK_DIR/$ZIP_NAME
	if test -f "$FILE"
	then
		checkApplicationAndPushToTenant
		subscribe
		deleteReleaseFile
	else
		echo "[ERROR] Unable to find file $WORK_DIR/$ZIP_NAME"
	fi
}

downloadReleaseFromGit () {
		echo
		echo "[INFO] Downloading release file"
		echo
		response=$(curl -LO -s -w "HTTPSTATUS:%{http_code}" $RELEASE_URL)
		responseCode=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
		if [ $responseCode -eq 200 ]
		then
			echo "[INFO] Build file downloaded successfully"
		else
			echo "[ERROR] Build file download failed"
			exitOnErrorInBackendResponse $response
		fi
}

deleteReleaseFile () {
		echo
		echo "[INFO] Deleting release file"
		echo
		rm -rf ewon-flexy-integration.zip
}

installJqCommand () {
	if ! command -v jq &> /dev/null
	then
    	echo "[INFO] jq could not be found"
		echo "[INFO] installing jq command"
		response=$(curl -s -w "HTTPSTATUS:%{http_code}" -L -o /usr/bin/jq.exe "https://github.com/stedolan/jq/releases/latest/download/jq-win64.exe")
		responseCode=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
		if [ $responseCode -eq 200 ]
		then
			echo "[INFO] jq installed successfully"
		else
			echo "[ERROR] Failed to install jq"
			exitOnErrorInBackendResponse $response
		fi
	fi
}

verifyDeployPrerequisits () {
	result=0
	verifyParamSet "$IMAGE_NAME" "name"
	verifyParamSet "$DEPLOY_ADDRESS" "baseUrl"
	verifyParamSet "$DEPLOY_TENANT" "tenant"
	verifyParamSet "$DEPLOY_USER" "user"
	verifyParamSet "$DEPLOY_PASSWORD" "password"
	verifyParamSet "$RELEASE_URL" "releaseUrl"

	if [ "$result" == "1" ]
	then
		echo "[WARNING] Deployment skipped"
		exit 1
	fi
}

verifyParamSet (){
	if [ "x$1" == "x" ]
	then
		echo "[WARNING] Missing parameter: $2"
		result=1
	fi
}

checkApplicationAndPushToTenant () {
	authorization="Basic $(echo -n "$DEPLOY_USER:$DEPLOY_PASSWORD" | base64 -w 0)"

	checkSubscription
	if [ $IS_SUBSCRIBED == 1 ]
	then 
		getApplicationId
		if [ "x$APPLICATION_ID" == "xnull" ]
		then
			echo "[ERROR] Application with name $APPLICATION_NAME not found, creating new application"
			createApplication $authorization
			getApplicationId
			if [ "x$APPLICATION_ID" == "xnull" ]
			then
				echo "[ERROR] Could not create application"
				exit 1
			fi
		fi
		echo "[INFO] Application name: $APPLICATION_NAME id: $APPLICATION_ID"
		uploadFile
	fi
		
}

checkSubscription () {
	echo
	echo "[INFO] Checking For Subscription"
	echo
	subscriptionName="feature-microservice-hosting"
	URL="$DEPLOY_ADDRESS/application/applicationsByName/$subscriptionName"
	response=$(curl -s -w "HTTPSTATUS:%{http_code}" $URL -H "Authorization: $authorization")

	responseCode=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
	responseBody=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
	name=$(echo "$responseBody" | jq -r .applications[0].name)
	
	if [ $responseCode -eq 200 ] && [ $name == $subscriptionName ]
	then
		IS_SUBSCRIBED=1
		echo "[INFO] Microservice $APPLICATION_NAME is subscribed"
	else
		echo "[ERROR] Microservice $APPLICATION_NAME is not subscribed"
	fi
}

getApplicationId () {
	echo
	echo "[INFO] Fetching Application Id"
	echo
	URL="$DEPLOY_ADDRESS/application/applicationsByName/$APPLICATION_NAME"
	response=$(curl -s -w "HTTPSTATUS:%{http_code}" $URL -H "Authorization: $authorization")

	responseCode=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
	responseBody=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
	if [ $responseCode -eq 200 ]
	then
		APPLICATION_ID=$(echo "$responseBody" | jq -r .applications[0].id)
	else
		echo "[ERROR] Application $APPLICATION_NAME not found"
		exitOnErrorInBackendResponse $response
	fi
}

createApplication () {
	echo
	echo "[INFO] Creating Application"
	echo

	if [ "$IS_FRONTEND" == "1" ]
	then
		body="{
			\"name\": \"$APPLICATION_NAME\",
			\"type\": \"HOSTED\",
			\"key\": \"$APPLICATION_NAME-application-key\",
			\"contextPath\": \"$APPLICATION_NAME\",
			\"resourcesUrl\": \"/\"
		}"
	else
		body="{
				\"name\": \"$APPLICATION_NAME\",
				\"type\": \"MICROSERVICE\",
				\"key\": \"$APPLICATION_NAME-microservice-key\"
			}"
	fi
	response=$(curl -w "HTTPSTATUS:%{http_code}" -X POST -s -S -d "$body" -H "Authorization: $authorization"  -H "Content-type: application/json" "$DEPLOY_ADDRESS/application/applications")
	responseCode=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
	if [ $responseCode -eq 201 ]
	then
		echo "[INFO] Application $APPLICATION_NAME successfully created"
	else
		echo "[ERROR] Failed to create application"
		exitOnErrorInBackendResponse $response
	fi
}

uploadFile () {
	echo
	echo "[INFO] Upload file $ZIP_NAME to Tenant $DEPLOY_TENANT for application $APPLICATION_NAME"
	echo
	echo "$DEPLOY_ADDRESS/application/applications/$APPLICATION_ID/binaries"
	response=$(curl -w "HTTPSTATUS:%{http_code}" -F "data=@$WORK_DIR/$ZIP_NAME" -H "Authorization: $authorization"  "$DEPLOY_ADDRESS/application/applications/$APPLICATION_ID/binaries")
	responseCode=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
	if [ $responseCode -eq 201 ]
	then
		echo "[INFO] File uploaded"
		if [ "$IS_FRONTEND" == "1" ]
		then
			activateFrontendApp
		fi
	else
		echo "[ERROR] File upload failed"
		echo $response
		exitOnErrorInBackendResponse $response
	fi
}

activateFrontendApp () {
	response=$(curl -w "HTTPSTATUS:%{http_code}" -H "Authorization: $authorization"  "$DEPLOY_ADDRESS/application/applications/$APPLICATION_ID/binaries?pageSize=100")
	responseCode=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
	responseBody=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
	if [ $responseCode -eq 200 ]
	then
		activateBinaryId=$(echo "$responseBody" | jq -r .attachments[5].id)
		body="{
				\"id\": \"$APPLICATION_ID\",
				\"activeVersionId\": \"$activateBinaryId\"
			}"
		response=$(curl -w "HTTPSTATUS:%{http_code}" -X PUT -s -S -d "$body" -H "Authorization: $authorization"  -H "Content-type: application/json" "$DEPLOY_ADDRESS/application/applications/$APPLICATION_ID")
	fi
}

subscribe () {
	echo
	echo "[INFO] Tenant $DEPLOY_TENANT subscription to application $APPLICATION_NAME"
	echo
	verifySubscribePrerequisits
	authorization="Basic $(echo -n "$DEPLOY_USER:$DEPLOY_PASSWORD" | base64 -w 0)"

	body="{\"application\":{\"id\": \"$APPLICATION_ID\"}}"
	response=$(curl -w "HTTPSTATUS:%{http_code}" -X POST -s -S -d "$body"  -H "Authorization: $authorization"  -H "Content-type: application/json" "$DEPLOY_ADDRESS/tenant/tenants/$DEPLOY_TENANT/applications")
	responseCode=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
	if [ $responseCode -eq 201 ] || [ $responseCode -eq 409 ]
	then
		echo "[INFO] Tenant $DEPLOY_TENANT subscribed to application $APPLICATION_NAME"
	else
		echo "[ERROR] Tenant $DEPLOY_TENANT subscription to application $APPLICATION_NAME failed"
		exitOnErrorInBackendResponse $response
	fi
}

verifySubscribePrerequisits () {
	if [ "x$APPLICATION_ID" == "x" ]
	then
		echo "[ERROR] Subscription not possible, unknown applicationId"
		exit 1
	fi
	verifyDeployPrerequisits
}

exitOnErrorInBackendResponse() {
	RESPONSE_ERROR=$(echo $1)
	if [ "x$RESPONSE_ERROR" != "xnull" ] && [ "x$RESPONSE_ERROR" != "x" ]
	then
		echo "[ERROR] Error while communicating with platform. Error message: $(echo $1 | jq -r .message)"
		echo "[ERROR] Full response: $1"
		echo "[ERROR] HTTP CODE: $HTTP_CODE"
		deleteReleaseFile
		exit 1
	fi
}

execute $@