ARG Platform="amd64"

FROM scmxzhaw/texlive-full:$Platform

# install dependencies
RUN apt update && apt install -y python3.8 pip poppler-utils git

# clone repository
RUN git clone https://github.com/felix-schmitt/FormulaNet.git

# prepare python env
WORKDIR FormulaNet/
RUN pip install -r requirements.txt

CMD ["python3", "./download.py"]