# Describes a trained machine learning model 
This Item describe a trained machine learning model using [mlm](https://github.com/stac-extensions/mlm) STAC extension.

For creating the environment and executing the Jupyter Notebook needed for this scenario, open a new terminal and execute the following commands:  

```
mamba env create -f environment.yml
conda activate mlm
python -m ipykernel install --user --name "mlm"
```

You might need to refresh your window, then open the **[Describe-MLmodel.ipynb](Describe-MLmodel.ipynb)** Notebook and select the `mlm` kernel on the top-right side of the window.