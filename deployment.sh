#!/bin/bash

WORK_DIR=$(pwd)
APPLICATION_NAME=
TAG_NAME="latest"
DEPLOY_ADDRESS=
DEPLOY_TENANT=
DEPLOY_USER=
DEPLOY_PASSWORD=
APPLICATION_ID=
IS_SUBSCRIBED=0

PACK=1
DEPLOY=1
SUBSCRIBE=1
HELP=1

execute () {
	set -e
	readInput $@
	cd $WORK_DIR
	if [ "$HELP" == "0" ]
	then
		printHelp
		exit
	fi
	if [ "$DEPLOY" == "1" ]
	then
		echo "[INFO] No goal set. Please set deploy"
	fi
	if [ "$DEPLOY" == "0" ]
	then
		echo "[INFO] Start deployment"
		deploy
		echo "[INFO] End deployment"
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
		pack)
		PACK=0
		shift
		;;	
		deploy)
		DEPLOY=0
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
		-d | --deploy)
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
		*)
		shift
		;;
	esac
	done
	setDefaults
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

deploy (){
	FILE=$WORK_DIR/$ZIP_NAME
	if test -f "$FILE"
	then
		verifyDeployPrerequisits
		checkApplicationAndPushToTenant
		subscribe
	else
		echo "[ERROR] Unable to find file $WORK_DIR/$ZIP_NAME"
	fi
}

verifyDeployPrerequisits () {
	result=0
	verifyParamSet "$IMAGE_NAME" "name"
	verifyParamSet "$DEPLOY_ADDRESS" "address"
	verifyParamSet "$DEPLOY_TENANT" "tenant"
	verifyParamSet "$DEPLOY_USER" "user"
	verifyParamSet "$DEPLOY_PASSWORD" "password"

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
			echo "[ERROR] Application with name $APPLICATION_NAME not found, create new application"
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
	body="{
			\"name\": \"$APPLICATION_NAME\",
			\"type\": \"MICROSERVICE\",
			\"key\": \"$APPLICATION_NAME-microservice-key\"
		}
	"
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
	else
		echo "[ERROR] File upload failed"
		exitOnErrorInBackendResponse $response
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
		echo "[ERROR] Error while communicating with platform. Error message: $(echo $resp | jq -r .message)"
		echo "[ERROR] Full response: $1"
		echo "[ERROR] HTTP CODE: $HTTP_CODE"
		exit 1
	fi
}

execute $@