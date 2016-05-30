# RPi-DoorController

This is a service to controll a door lock by a Raspberry Pi with a servo motor.  

## How to install?  

Run **git clone http://github.com/kalehmann/RPi-DoorController**. After that, go to **RPi-DoorController/src** and execute **sudo ./setup.sh install** to install and launch the *doorcontrollerservice*.  
Now connect a servo motor to the lock of your door (or create your own lock) and specify the gpio, the servo is connected to, the dutycycle to open the door and the dutycycle to close the door in **/etc/doorcontrollerservice/default.conf**.  
![ImageOfRPiWithLock](https://raw.githubusercontent.com/kalehmann/RPi-DoorController/master/media/03.png) 
It is also possible to place a button on the door, which detects whether the door is opened or closed.   
Selfmade button:  
![SelfmadeButtonOnDoor](https://raw.githubusercontent.com/kalehmann/RPi-DoorController/master/media/04.png)  
Simply edit **/etc/doorcontrollerservice/default.conf**, set *use_door_sensor* in the section *doorsensor* to true and change *sensor_gpio* to the gpio, your button is connected to.  
When the door gets opened now, all scripts in **/var/doorcontrollerservice/onOpened/** get executed and if the door gets closed all scripts in **/var/doorcontrollerservice/onClosed/**.  

Example wiring with servo and button:  
![WiringWithServoAndButton](https://raw.githubusercontent.com/kalehmann/RPi-DoorController/master/media/wiring.png)  
Finally install the RPi-Door.apk on your phone, enter the IP of the raspberry and have fun!  
(You can also write your own client using [this](https://github.com/kalehmann/RPi-DoorController/wiki/Writing-your-own-client) instructions.)
