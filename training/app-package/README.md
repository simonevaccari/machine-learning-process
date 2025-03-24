# Run Training Module using CWL Runner

In this section, the users have the option to execute their training remotely on a remote machine, which becomes their preferred choice for conducting long-running experiments. The application encompasses [make-ml-model](../make-ml-model/README.md) module. 
In general, the user will be able to train a simple training job and track evaluation metrics, model's hyper-parameters, application inputs, and artifacts using mlflow. For executing the application package, the user have the options to use whether [cwltool](https://github.com/common-workflow-language/cwltool) or [calrissian](https://github.com/Duke-GCB/calrissian).


## How to execute the application-package?
Before executing the application package with a CWL runner, the user must first update the [params.yaml](./params.yaml) with the correct credentials as well as updating the latest docker image reference in the cwl file as below:
```
cd training/app-package
VERSION="0.0.2"
curl -L -o "tile-sat-training.${VERSION}.cwl" \
  "https://github.com/parham-membari-terradue/machine-learning-process-new/releases/download/${VERSION}/tile-sat-training.${VERSION}.cwl"

```


### **Run the Application package**:
There are two methods to execute the application:

- Executing the tile-based-training using cwltool in a terminal:

    ```
    cwltool --podman --debug tile-sat-training.cwl#tile-sat-training params.yml
    ```
    


- Executing the tile-based classification using calrissian in a terminal:

    ```
    calrissian --debug --stdout /calrissian/out.json --stderr /calrissian/stderr.log --usage-report /calrissian/report.json --max-ram 10G --max-cores 2 --tmp-outdir-prefix /calrissian/tmp/ --outdir /calrissian/results/ --tool-logs-basepath /calrissian/logs tile-sat-training.cwl#tile-sat-training params.yaml
    ```

   

## Additional Resources
Please see below for additional resources and tutorials for developing Earth Observation (EO) Application Packages using the CWL:
* [Application Package and CWL as a solution for EO portability](https://eoap.github.io/cwl-eoap/)
* [A simple EO Application Package for getting started](https://eoap.github.io/quickwin/)
* [Mastering EO Application Packaging with CWL](https://eoap.github.io/mastering-app-package/)
* [Inference with the EO Application Package](https://eoap.github.io/inference-eoap/)