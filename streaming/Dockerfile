FROM public.ecr.aws/lambda/python:3.9

RUN yum install -y gcc python3-devel atlas-devel blas-devel lapack-devel

RUN pip install -U pip  

COPY requirements.txt ./

RUN pip install -r requirements.txt --no-cache-dir

COPY lambda_function.py ./

CMD [ "lambda_function.lambda_handler" ]
