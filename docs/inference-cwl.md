# Inference Module & CWL Runner

In the [training module](training-container.md), a CNN model was trained on the EuroSAT dataset to classify image chips into 10 different land use/land cover classes. The training workflow was tracked using MLflow.

This Application Package provides a CWL document that performs inference by applying the trained model to unseen Sentinel-2 data in order to generate a classified image. The CWL document contains a single main workflow that executes one `CommandLineTool` step. It also supports parallel execution by accepting a list of Sentinel-2 references as input, making it suitable for running at scale on a Minikube cluster.

To execute the application, users have the option to use either [cwltool](https://github.com/common-workflow-language/cwltool) or [Calrissian](https://github.com/Duke-GCB/calrissian) as the CWL runner.

## Inputs:
- `input_reference`: A list of reference to a Sentinel-2 product on [planetary computer](https://planetarycomputer.microsoft.com/api/stac/v1/collections). The application will give you an accurate result if the sentinel-2 product has no/low cloud-cover.

## How to Execute the Application Package

Before running the application with a CWL runner, make sure to download and use the latest version of the CWL document:

```bash
cd inference/app-package
VERSION=$(curl -s https://api.github.com/repos/eoap/machine-learning-process/releases/latest | jq -r '.tag_name')
curl -L -o "tile-sat-inference.cwl" \
  "https://github.com/eoap/machine-learning-process/releases/download/${VERSION}/tile-sat-inference.${VERSION}.cwl"
```

### **Run the Application Package**:
There are two methods to execute the application:

- Executing the `tile-sat-inference` app using `cwltool`:

    ```bash
    cwltool --podman --debug --parallel tile-sat-inference.cwl#tile-sat-inference params.yml
    ```

- Executing the `tile-sat-inference` using `calrissian`:

    ```bash
    
    calrissian --debug --stdout /calrissian/out.json --stderr /calrissian/stderr.log --usage-report /calrissian/report.json --max-ram 10G --max-cores 2 --parallel --tmp-outdir-prefix /calrissian/tmp/ --outdir /calrissian/results/ --tool-logs-basepath /calrissian/logs tile-sat-inference.cwl#tile-sat-inference params.yml
    ```
  > You can monitor the pod creation using command below:
  >
  >   `kubectl get pods` 

## How the CWL document designed:
The CWL file can be triggered using `cwltool` or `calrissian`. The user provides a `params.yml` file that passes all inputs needed by the CWL file to execute the module. The CWL file is designed to execute the module based on the structure below:

<p align="center"><img src="./imgs/inference.png" alt="Picture" width="40%" height="10%" style="display: block; margin: 20px auto;"/></p>

> **`[]`** in the image above indicates that the user may pass a list of parameters to the application package.

The Application Package will generate a list of directories containing intermediate or final output. The number of folders containing a `{STAC_ITEM_ID}_classified.tif` and the corresponding STAC objects, such as STAC Catalog and STAC Item, depends on the number of input Sentinel-2 items.


