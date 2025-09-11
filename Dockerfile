# A grpc4bmi server for the `CEM` model.
FROM csdms/grpc4bmi:0.3.0

LABEL org.opencontainers.image.authors="Mark Piper <mark.piper@colorado.edu>"
LABEL org.opencontainers.image.source="https://github.com/csdms/cem-grpc4bmi"
LABEL org.opencontainers.image.url="https://hub.docker.com/r/csdms/cem-grpc4bmi"
LABEL org.opencontainers.image.vendor="CSDMS"

RUN conda install -y \
    "cmake>=4.0" \
    "glib=2" \
    && conda clean --all -y

RUN git clone --branch v0 --depth 1 https://github.com/csdms-contrib/cem /opt/cem
WORKDIR /opt/cem/_build
RUN cmake .. -DCMAKE_INSTALL_PREFIX=${CONDA_DIR} && \
    make && \
    ctest -V && \
    make install && \
    make clean

COPY server /opt/cem-grpc4bmi-server
WORKDIR /opt/cem-grpc4bmi-server/_build
RUN cmake .. -DCMAKE_INSTALL_PREFIX=${CONDA_DIR} && \
    make && \
    make install && \
    make clean

WORKDIR /opt

ENTRYPOINT ["/opt/conda/bin/cem-grpc4bmi-server"]
EXPOSE 55555
