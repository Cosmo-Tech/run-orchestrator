if [ -e "Simulation/Resource/scenariorun-data.back" ] || [ -L "Simulation/Resource/scenariorun-data.back" ]; then
  rm Simulation/Resource/scenariorun-data 
  mv Simulation/Resource/scenariorun-data.back Simulation/Resource/scenariorun-data 
fi