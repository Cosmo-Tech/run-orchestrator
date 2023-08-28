if [ -e "Simulation/Resource/scenariorun-data" ] || [ -L "Simulation/Resource/scenariorun-data" ]; then
  mv Simulation/Resource/scenariorun-data Simulation/Resource/scenariorun-data.back
fi 
ln -s $(realpath $CSM_DATASET_ABSOLUTE_PATH) Simulation/Resource/scenariorun-data