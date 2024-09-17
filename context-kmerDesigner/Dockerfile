# install Python and requirements
FROM ashsmol/python312
# update systen
RUN apt-get update -y
RUN apt-get upgrade -y
# install wget
RUN apt-get install wget
# upgrade pip
RUN pip install --upgrade pip
# sets the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions
WORKDIR /context-kmerDesigner
# copy the script
COPY kmerDesigner.py ./
# add the Python requirements
ADD requirements.txt ./
# install Python requirements
RUN pip install -r /context-kmerDesigner/requirements.txt
# set entrypoint
ENTRYPOINT  ["python3.12", "/context-kmerDesigner/kmerDesigner.py"]
# sets the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions
WORKDIR /wd
# get the usage when launching rather the help
CMD ["/bin/bash"]
