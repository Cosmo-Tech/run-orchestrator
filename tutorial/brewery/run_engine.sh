if [ -d "Simulation/Resource/scenariorun-data" ]; then
  mv Simulation/Resource/scenariorun-data/ Simulation/Resource/scenariorun-data.back
fi
cp -r $CSM_DATASET_ABSOLUTE_PATH Simulation/Resource/scenariorun-data
csm-run-orchestrator run-step --template what_if --steps engine
if [ -d "Simulation/Resource/scenariorun-data.back" ]; then
  rm -rf Simulation/Resource/scenariorun-data/ 
  mv Simulation/Resource/scenariorun-data.back Simulation/Resource/scenariorun-data 
fi