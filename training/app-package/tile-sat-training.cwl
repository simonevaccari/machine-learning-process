cwlVersion: v1.2
$namespaces:
  s: https://schema.org/
s:softwareVersion: 1.0.8 
schemas:
  - http://schema.org/version/9.0/schemaorg-current-http.rdf
$graph:
  - class: Workflow
    id: tile-sat-training
    label: Tile-based calssifier on EuroSAT data
    doc: Training a CNN on Sentinel-2 data(EuroSAT) to classify small patch of image into different landcover classes.    
    requirements:
      - class: InlineJavascriptRequirement
      - class: ScatterFeatureRequirement
    inputs:
      MLFLOW_TRACKING_URI: 
        label: MLFLOW_TRACKING_URI
        type: string
      stac_reference:
        label: stac_reference
        doc: STAC Item label url
        type: string
      BATCH_SIZE:
        label: BATCH_SIZE
        default: 4
        doc: BATCH_SIZE- model metadata
        type: int[]
      CLASSES:
        label: CLASSES
        default: 10
        doc: CLASSES- model metadata
        type: int
      DECAY:
        label: DECAY
        default: 0.1
        doc: DECAY- model metadata
        type: float[]
      EPOCHS:
        label: EPOCHS
        default: 5
        doc: EPOCHS- model metadata
        type: int[]
      EPSILON:
        label: EPSILON
        default: 0.000002
        doc: EPSILON- model metadata
        type: float[]
      LEARNING_RATE:
        label: LEARNING_RATE
        default: 0.0001
        doc: LEARNING_RATE- model metadata
        type: float[]
      LOSS:
        label: LOSS
        default: "categorical_crossentropy"
        doc: LOSS- model metadata
        type: string[]
      
      MEMENTUM:
        label: MEMENTUM
        default: 0.95
        doc: MEMENTUM- model metadata
        type: float[]
      OPTIMIZER:
        label: OPTIMIZER
        default: "Adam"
        doc: OPTIMIZER- model metadata
        type: string[]
      REGULARIZER:
        label: REGULARIZER
        default: "None"
        doc: REGULARIZER- model metadata
        type: string[]
      
      SAMPLES_PER_CLASS:
        label: SAMPLES_PER_CLASS
        default: 500
        doc: SAMPLES_PER_CLASS- model metadata
        type: int
      
    outputs: 
      - id: artifacts
        outputSource: 
          - training/artifacts
        type: Directory[]
    steps:
      training:
        run: "#training"
        in:  
          MLFLOW_TRACKING_URI: MLFLOW_TRACKING_URI
          stac_reference: stac_reference
          BATCH_SIZE: BATCH_SIZE
          CLASSES: CLASSES
          DECAY: DECAY
          EPOCHS: EPOCHS
          EPSILON: EPSILON
          LEARNING_RATE: LEARNING_RATE
          LOSS: LOSS  
          MEMENTUM: MEMENTUM
          OPTIMIZER: OPTIMIZER
          REGULARIZER: REGULARIZER
          SAMPLES_PER_CLASS: SAMPLES_PER_CLASS
        scatter: 
          - BATCH_SIZE
          - DECAY
          - EPOCHS
          - EPSILON
          - LEARNING_RATE
          - LOSS
          - MEMENTUM
          - OPTIMIZER
          - REGULARIZER

        scatterMethod: dotproduct # "flat_crossproduct" to analyse all possible combination of inputs
        out: 
          - artifacts
        
      
  - class: CommandLineTool
    id: training
    requirements:
      InlineJavascriptRequirement: {}
      NetworkAccess:
        networkAccess: true
      EnvVarRequirement:
        envDef:
          #LD_LIBRARY_PATH: /home/neo/.local/share/hatch/env/virtual/.pythons/3.10/python/lib/libpython3.10.so.1.0
          #PATH: /home/neo/.local/bin:/home/neo/bin:/code/envs/env_5/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
          MLFLOW_TRACKING_URI: $(inputs.MLFLOW_TRACKING_URI)
      ResourceRequirement:
        coresMax: 1
        ramMax: 4096
    hints:
      DockerRequirement:
        dockerPull: train:latest 
        
    baseCommand: ["tile-based-training"]
    arguments: []
      
      # - valueFrom: |
      #       ${
      #           var args=[];
      #           for (var i = 0; i < inputs.IMAGE_SIZE.length; i++)
      #           {
      #             args.push("--IMAGE_SIZE");
      #             args.push(inputs.IMAGE_SIZE[i]);
      #           }
      #           return args;
      #       }
    inputs:
      MLFLOW_TRACKING_URI:
        type: string  
      stac_reference:
        type: string
        inputBinding:
          prefix: --stac_reference
      BATCH_SIZE:
        type: int
        inputBinding:
          prefix: --BATCH_SIZE
      CLASSES:
        type: int
        inputBinding:
          prefix: --CLASSES
      DECAY:
        type: float
        inputBinding:
          prefix: --DECAY
      EPOCHS:
        type: int
        inputBinding:
          prefix: --EPOCHS
      EPSILON:
        type: float
        inputBinding:
          prefix: --EPSILON
      LEARNING_RATE:
        type: float
        inputBinding:
          prefix: --LEARNING_RATE
      LOSS:
        type: string
        inputBinding:
          prefix: --LOSS
      
      MEMENTUM:
        type: float
        inputBinding:
          prefix: --MEMENTUM
      OPTIMIZER:
        type: string
        inputBinding:
          prefix: --OPTIMIZER
      REGULARIZER:
        type: string
        inputBinding:
          prefix: --REGULARIZER
      
      SAMPLES_PER_CLASS:
        type: int
        inputBinding:
          prefix: --SAMPLES_PER_CLASS
      
      

    outputs: 
      artifacts:
        outputBinding:
          glob: .
        type: Directory

  