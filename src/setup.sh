#! /bin/bash

SERVICE_DIR="/opt/doorcontrollerservice"

print_usage() {
  echo "Error, usage : $0 install|uninstall" 
}

if [ "$1" == "install" ]; then

  echo "Installing doorcontrollerservice . . ."

  if [ ! -d $SERVICE_DIR ]; then
    mkdir $SERVICE_DIR
  fi

  cp main.py              $SERVICE_DIR
  cp default_start_config $SERVICE_DIR
  cp default_start_config /etc/default/doorcontrollerservice
  cp default_config       $SERVICE_DIR
  cp default_config       /etc/doorcontrollerservice/default.conf
  mkdir /var/doorcontrollerservice/
  mkdir /var/doorcontrollerservice/onOpened
  mkdir /var/doorcontrollerservice/onClosed

elif [ "$1" == "uninstall" ]; then

  echo "Uninstalling doorcontrollerservice . . ."

  rm -R $SERVICE_DIR
  rm -R /var/doorcontrollerservice
  rm /etc/default/doorcontrollerservice
  rm /etc/doorcontrollerservice/default.conf
  rm /var/log/doorcontrollerservice.log
  rm /var/run/doorcontrollerservice.pid

else
  print_usage
  exit
fi

echo "Done."
