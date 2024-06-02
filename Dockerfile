FROM amancevice/pandas
RUN echo 'Install jira python library' && pip install jira
RUN echo 'Install openpyxl library' && pip install openpyxl
RUN echo 'Install lxml library' && pip install lxml
CMD ["python", "/tmp/bin/server.py"]
