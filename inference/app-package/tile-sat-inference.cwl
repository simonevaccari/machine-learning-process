cwlVersion: v1.2
$namespaces:
  s: https://schema.org/
s:softwareVersion: 1.0.8
schemas:
  - http://schema.org/version/9.0/schemaorg-current-http.rdf
$graph:
  - class: Workflow
    id: tile-sat-inference
    label: Tile-SAT Inference on Sentinel-2 L1C data
    doc: A trained CNN model performs a tile-based inference on Sentinel-2 L1C data to classify image into 11 different classes.
    requirements:
      - class: InlineJavascriptRequirement
      - class: ScatterFeatureRequirement
      - class: SubworkflowFeatureRequirement
    inputs:
      input_reference:
        doc: S2 product
        label: S2 product
        type: Directory
    outputs:
      results:
        outputSource:
        - make_inference/artifacts
        type: Directory
    steps:
      make_inference:
        in:
          input_reference: input_reference
        out:
        - artifacts
        run: '#make_inference'

  - class: CommandLineTool
    id: make_inference
    hints:
      DockerRequirement:
        dockerPull: tile-sat-inference:latest
    baseCommand: ["make-inference"]
    inputs:
      input_reference:
        type: Directory
        inputBinding:
          position: 1
          prefix: --input_reference
    outputs:
      artifacts:
        outputBinding:
          glob: .
        type: Directory
    requirements:
      InlineJavascriptRequirement: {}
      NetworkAccess:
        networkAccess: true
      ResourceRequirement:
        coresMax: 1
        ramMax: 3000
