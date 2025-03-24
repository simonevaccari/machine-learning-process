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
      ADES_AWS_S3_ENDPOINT: 
        label: ADES_AWS_S3_ENDPOINT
        type: string?
      ADES_AWS_REGION: 
        label: ADES_AWS_REGION
        type: string?
      ADES_AWS_DEFAULT_REGION: 
        label: ADES_AWS_DEFAULT_REGION
        type: string?
      ADES_AWS_ACCESS_KEY_ID: 
        label: ADES_AWS_ACCESS_KEY_ID
        type: string?
      ADES_AWS_SECRET_ACCESS_KEY: 
        label: ADES_AWS_SECRET_ACCESS_KEY
        type: string?
      ADES_BUCKET_NAME: 
        label: ADES_BUCKET_NAME
        type: string?
      ADES_IAM_URL: 
        label: ADES_IAM_URL
        type: string?
      ADES_IAM_PASSWORD: 
        label: ADES_IAM_PASSWORD
        type: string?
      MLFLOW_TRACKING_URI: 
        label: MLFLOW_TRACKING_URI
        type: string
      stac_endpoint_url:
        label: stac_endpoint_url
        doc: STAC Item label url
        type: string


      BATCH_SIZE:
        label: BATCH_SIZE
        default: 4
        doc: BATCH_SIZE- model metadata
        type: int
      EPOCHS:
        label: EPOCHS
        default: 5
        doc: EPOCHS- model metadata
        type: int
      LEARNING_RATE:
        label: LEARNING_RATE
        default: 0.0001
        doc: LEARNING_RATE- model metadata
        type: float
      DECAY:
        label: DECAY
        default: 0.1
        doc: DECAY- model metadata
        type: float
      EPSILON:
        label: EPSILON
        default: 0.000002
        doc: EPSILON- model metadata
        type: float
      MEMENTUM:
        label: MEMENTUM
        default: 0.95
        doc: MEMENTUM- model metadata
        type: float
      LOSS:
        label: LOSS
        default: "categorical_crossentropy"
        doc: LOSS- model metadata
        type: string
      REGULIZER:
        label: REGULIZER
        default: "None"
        doc: REGULIZER- model metadata
        type: string
      OPTIMIZER:
        label: OPTIMIZER
        default: "Adam"
        doc: OPTIMIZER- model metadata
        type: string
      SAMPLES_PER_CLASS:
        label: SAMPLES_PER_CLASS
        default: 500
        doc: SAMPLES_PER_CLASS- model metadata
        type: int
      CLASSES:
        label: CLASSES
        default: 10
        doc: CLASSES- model metadata
        type: int
      IMAGE_SIZE:
        label: IMAGE_SIZE
        doc: IMAGE_SIZE- model metadata
        type: int[]
      enable_data_ingestion:
        label: enable_data_ingestion
        default: "False"
        doc: A flag to enable data ingestion pipeline
        type: boolean
    outputs: 
      - id: artifacts
        outputSource: 
          - training/artifacts
        type: Directory[]
    steps:
      training:
        run: "#training"
        in:  
          ADES_AWS_S3_ENDPOINT: ADES_AWS_S3_ENDPOINT
          ADES_AWS_REGION: ADES_AWS_REGION
          ADES_AWS_DEFAULT_REGION: ADES_AWS_DEFAULT_REGION
          ADES_AWS_ACCESS_KEY_ID: ADES_AWS_ACCESS_KEY_ID
          ADES_AWS_SECRET_ACCESS_KEY: ADES_AWS_SECRET_ACCESS_KEY
          ADES_BUCKET_NAME: ADES_BUCKET_NAME
          ADES_IAM_URL: ADES_IAM_URL
          ADES_IAM_PASSWORD: ADES_IAM_PASSWORD
          MLFLOW_TRACKING_URI: MLFLOW_TRACKING_URI
          stac_endpoint_url: stac_endpoint_url
          BATCH_SIZE: BATCH_SIZE
          EPOCHS: EPOCHS
          LEARNING_RATE: LEARNING_RATE
          DECAY: DECAY
          EPSILON: EPSILON
          MEMENTUM: MEMENTUM
          LOSS: LOSS  
          REGULIZER: REGULIZER
          OPTIMIZER: OPTIMIZER
          SAMPLES_PER_CLASS: SAMPLES_PER_CLASS
          CLASSES: CLASSES
          IMAGE_SIZE: IMAGE_SIZE
          enable_data_ingestion: enable_data_ingestion

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
          AWS_S3_ENDPOINT: $( inputs.ADES_AWS_S3_ENDPOINT )
          AWS_REGION: $( inputs.ADES_AWS_REGION )
          AWS_DEFAULT_REGION: $(inputs.ADES_AWS_DEFAULT_REGION ) 
          AWS_ACCESS_KEY_ID: $( inputs.ADES_AWS_ACCESS_KEY_ID )
          AWS_SECRET_ACCESS_KEY: $( inputs.ADES_AWS_SECRET_ACCESS_KEY )
          BUCKET_NAME: $( inputs.ADES_BUCKET_NAME )            
          IAM_URL: $( inputs.ADES_IAM_URL ) 
          IAM_PASSWORD: $( inputs.ADES_IAM_PASSWORD ) 
          MLFLOW_TRACKING_URI: $(inputs.MLFLOW_TRACKING_URI)
      ResourceRequirement:
        coresMax: 1
        ramMax: 1600
    hints:
      DockerRequirement:
        dockerPull: training:latest 
        
    baseCommand: ["tile-based-training"]
    arguments: 
      
      - valueFrom: |
            ${
                var args=[];
                for (var i = 0; i < inputs.IMAGE_SIZE.length; i++)
                {
                  args.push("--IMAGE_SIZE");
                  args.push(inputs.IMAGE_SIZE[i]);
                }
                return args;
            }
    inputs:
      ADES_AWS_S3_ENDPOINT:
        type: string?
        
      ADES_AWS_DEFAULT_REGION:
        type: string?
        

      ADES_AWS_REGION:
        type: string?
        
      ADES_AWS_ACCESS_KEY_ID:
        type: string?
        
      ADES_AWS_SECRET_ACCESS_KEY:
        type: string?
        
      ADES_BUCKET_NAME:
        type: string?
        
      ADES_IAM_URL:
        type: string?
        
      ADES_IAM_PASSWORD:
        type: string?
      MLFLOW_TRACKING_URI:
        type: string  
      stac_endpoint_url:
        type: string
        inputBinding:
          prefix: --stac_endpoint_url
      BATCH_SIZE:
        type: int
        inputBinding:
          prefix: --BATCH_SIZE
      EPOCHS:
        type: int
        inputBinding:
          prefix: --EPOCHS
      LEARNING_RATE:
        type: float
        inputBinding:
          prefix: --LEARNING_RATE
      DECAY:
        type: float
        inputBinding:
          prefix: --DECAY
      EPSILON:
        type: float
        inputBinding:
          prefix: --EPSILON
      MEMENTUM:
        type: float
        inputBinding:
          prefix: --MEMENTUM
      LOSS:
        type: string
        inputBinding:
          prefix: --LOSS
      REGULIZER:
        type: string
        inputBinding:
          prefix: --REGULIZER
      OPTIMIZER:
        type: string
        inputBinding:
          prefix: --OPTIMIZER
      SAMPLES_PER_CLASS:
        type: int
        inputBinding:
          prefix: --SAMPLES_PER_CLASS
      CLASSES:
        type: int
        inputBinding:
          prefix: --CLASSES
      IMAGE_SIZE:
        type: int[]
        
      enable_data_ingestion:
        type: boolean
        inputBinding:
          prefix: --enable_data_ingestion

    outputs: 
      artifacts:
        outputBinding:
          glob: .
        type: Directory[]

  