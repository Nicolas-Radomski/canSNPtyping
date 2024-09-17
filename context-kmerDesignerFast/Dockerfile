# install Python and requirements
FROM ashsmol/python312
# upgrade pip
RUN pip install --upgrade pip
# sets the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions
WORKDIR /context-kmerDesignerFast
# copy the script
COPY kmerDesignerFast.py ./
# add the Python requirements
ADD requirements.txt ./
# install Python requirements
RUN pip install -r /context-kmerDesignerFast/requirements.txt
# set entrypoint
ENTRYPOINT  ["python3.12", "/context-kmerDesignerFast/kmerDesignerFast.py"]
# sets the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions
WORKDIR /wd
# get the usage when launching rather the help
CMD ["/bin/bash"]
