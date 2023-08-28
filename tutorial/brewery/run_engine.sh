if [ -e "Simulation/Resource/scenariorun-data" ] || [ -L "Simulation/Resource/scenariorun-data" ]; then
  mv Simulation/Resource/scenariorun-data Simulation/Resource/scenariorun-data.back
fi 
ln -s $(realpath $CSM_DATASET_ABSOLUTE_PATH) Simulation/Resource/scenariorun-data
csm-run-orchestrator run-step --template what_if --steps engine
if [ -e "Simulation/Resource/scenariorun-data.back" ] || [ -L "Simulation/Resource/scenariorun-data.back" ]; then
  rm Simulation/Resource/scenariorun-data 
  mv Simulation/Resource/scenariorun-data.back Simulation/Resource/scenariorun-data 
fi