FROM conda/miniconda3:latest

RUN cd
RUN mkdir kr
COPY . kr
WORKDIR kr
#RUN conda update conda
RUN conda env create --file=env.yaml
RUN source activate kessel_run
#RUN python data_generation/mongo_wmata_data.py