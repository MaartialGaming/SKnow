STEP 1 - CONFIGURATION

- navigate to the extracted folder (the folder containing this file) and open thingspeak_connector/_ThingspeakConnectorSettings.json, then populate the "user_key" field with a valid Thingspeak user key (https://it.mathworks.com/help/thingspeak/users-and-channels.html)

- navigate to the extracted folder (the folder containing this file) and open telegram_bot/_TelegramBotSettings.json, then populate the "token" field with a valid Telegram Bot token (https://core.telegram.org/bots/api#authorizing-your-bot)



STEP 2 - STARTUP

- Make sure Docker engine is running (i.e. open Docker Desktop)

- open a terminal and navigate to the extracted folder (the folder containing this file), then run the following set of commands:
    - to build the Docker images:
```
        docker-compose -f docker-compose-structure.yml build
```
    - to create and run the Docker volumes and containers concerning SKnow main structure (all the microservices):
```
        docker-compose -f docker-compose-structure.yml up -d
```



STEP 3 - PERSONALIZATION

- in the same terminal you can run the following command in order to run users' sensors and cannons:
    - to build the Docker images:
```
        docker-compose -f docker-compose-sensors-cannons.yml build
```
    - to create and run the containers:
```
        docker-compose -f docker-compose-sensors-cannons.yml up -d
```

- the sensors and cannons that are now running in the system are just a sample set to demonstrate the basic funcionalities. In order to properly use them in the network, go to STEP 4 and use the SKnow website to create a location called "Bardonecchia", with a slope called "SlopeA" that has a sector called "SectorX".

- in order to customize the set of sensors and cannons that join the network, you can modify the sample set (modify the docker-compose-sensors-cannons.yml file contained in the same folder of this file) or add other groups of devices (create a new configuration file). Either way, this must be the basic backbone of the .yml file:

```
    version: '3'

    services:

        ...

    volumes:
        shared-data:
            driver: local
            driver_opts:
                type: none
                o: bind
                device: shared

    networks:
        SKnow:
            external: true
```

- you must substitute the '...' with one or more definitions of a cannon or sensor.

- for a cannon, this is the syntax:

```
        <CONTAINER NAME>:
            container_name: <CONTAINER NAME>
            build:
                context: ./snow_cannon_device_connector
            volumes:
                - shared-data:/shared
            restart: always
            environment:
                id: <CANNON NAME>
                user: <USER>
                locality: <LOCALITY>
                slope: <SLOPE>
                sector: <SECTOR>
            networks:
                - SKnow
  ```

- for a sensor, this is the syntax:

```
        <CONTAINER NAME>:
            container_name: <CONTAINER NAME>
            build:
                context: ./sensor_device_connector
            volumes:
                - shared-data:/shared
            restart: always
            environment:
                id: <SENSOR NAME>
                user: <USER>
                locality: <LOCALITY>
                slope: <SLOPE>
                sector: <SECTOR>
                cannon: <REFERENCE CANNON>
                type: <MEASUREMENT TYPE>
                unit: <MEASUREMENT UNIT>
            networks:
            -    SKnow
  ```

- you must subtitute the text contained in <> accordingly:
    - for both of them:
        - CONTAINER NAME, CANNON NAME and SENSOR NAME can be any unique string
        - USER is the user id provided to the user when registering for the service - for testing use USER_804213822b8240d8801d9f554d9b2855
        - LOCALITY, SLOPE and SECTOR must refer to a registered location in the network
    - for the sensors:
        - REFERENCE CANNON must correspond to a CANNON NAME of a cannon if the sensor is measuring "water_level", otherwise it must be "None"
        - MEASUREMENT TYPE must be one among the available type of sensors: "water_level", "snow_depth", "temperature", "humidity"
        - MEASUREMENT UNIT is the unit for the measurement (e.g. "%", "mm", "°C", ...)



STEP 4 - MANAGEMENT AND CONTROL

- in order to modify the network structure (localities, slopes, sectors) and visualize the sensors data, you can access the SKnow website at http://127.0.0.1:8080/ and login using the token provided to the client during registration - for testing use 4f2fd6e33a4d42a1a66a9a617dcad43c

- in order to monitor and control the cannons and receive important notifications, you can access the SKnow bot (which, for security reasons, is the bot for which a token was provided in the second step of this tutorial) and login using the token provided to the client during registration - for testing use 4f2fd6e33a4d42a1a66a9a617dcad43c



STEP 5 - REGISTER ADDITIONAL USERS

- in order to add an additional user (task only the SKnow managers can perform), perform a POST request to the Login microservice at the following link (make sure the body of the requests is json-formatted and has the 'id' field populated with a string that will compose part of the user id)
    http://127.0.0.1:8083/L/user

- the requests will return a json with two keys: 'id' will identify the user id (needed as info for cannons and sensors), 'tok' will identify the token needed for accessing the SKnow web server and the SKnow telegram bot



STEP 6 - SHUT DOWN

- in order to shut down the network, run the following commands:
    - to remove sensors and cannons:
```
        docker-compose -f docker-compose-sensors-cannons.yml down
```
    - to then shut down the whole SKnow service:
```
        docker-compose -f docker-compose-structure.yml down
```
