# cem-grpc4bmi

Set up a [grpc4bmi](https://grpc4bmi.readthedocs.io) server
to run a containerized version
of the [CEM](https://csdms.colorado.edu/wiki/Model:CEM) model
through Python.

## Build

Build this example locally with:
```
docker build --tag cem-grpc4bmi .
```
The image is built on the [csdms/grpc4bmi](https://hub.docker.com/r/csdms/grpc4bmi) base image,
which is built on the [condaforge/miniforge3](https://hub.docker.com/r/condaforge/miniforge3) base image.
The OS is Linux/Ubuntu.
The CEM model, grpc4bmi, and the grpc4bmi server are installed in `/opt/conda`.
The CEM grpc4bmi server is exposed through port 55555.

## Run

Use the grpc4bmi Docker client to access the BMI methods of the containerized model.

Install with *pip*:
```
pip install grpc4bmi
```
Then, in a Python session, access CEM in the image built above with:
```python
from grpc4bmi.bmi_client_docker import BmiClientDocker


m = BmiClientDocker(image="cem-grpc4bmi", image_port=55555, work_dir=".")
m.get_component_name()

del m  # stop container cleanly
```

If the image isn't found locally, it's pulled from Docker Hub
(e.g., try the `csdms/cem-grpc4bmi` image).

For more in-depth examples of running the CEM model through grpc4bmi,
see the [examples](./examples) directory.

## Acknowledgment

This work is supported by the U.S. National Science Foundation under Award No. [2103878](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2103878), *Frameworks: Collaborative Research: Integrative Cyberinfrastructure for Next-Generation Modeling Science*.
