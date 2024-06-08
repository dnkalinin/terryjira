#!/usr/bin/python3.13
import pandas as pd
from io import BytesIO
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi, yaml, re, traceback, json, time, sys
from datetime import datetime, timedelta
from jira import JIRA

class RequestHandler(BaseHTTPRequestHandler):
    config = {}

    def initconfig(self):
        print('Reading config...')
        with open('/tmp/bin/config.yaml') as file:
            self.config = yaml.safe_load(file)

    def getconfig(self):
        return self.config

    def do_GET(self):

        # Cache request
        path = self.path

        # Validate request path, and set type
        if path == "/init":
            type = "text/html; charset=utf-8"
        elif path == "/html/index.html":
            type = "text/html"
        elif re.search("/html/styles", path):
            type = "text/css"
        elif re.search("/html/js", path):
            type = "text/javascript"
        elif path == "/html/images/favicon.ico":
            type = "image/x-icon"
        elif re.search("/html/images/.*\.png", path):
            type = "image/png"
        else:
            # Wild-card/default
            if not path == "/":
                print("UNRECONGIZED REQUEST: ", path)
            
            path = "/html/index.html"
            type = "text/html"

        self.send_response(200)
        self.send_header("Content-type", type)
        self.end_headers()

        # Open the file, read bytes, serve
        if path == "/init":
            self.initconfig()
            self.wfile.write(json.dumps(self.config).encode('utf-8'))
        else:
            with open(path, 'rb') as file: 
                self.wfile.write(file.read()) # Send

    def do_POST(self):
        self.initconfig()
        if self.path == '/upload':
            form = cgi.FieldStorage(
                fp = self.rfile,
                headers = self.headers,
                environ = {
                    'REQUEST_METHOD':'POST',
                    'CONTENT_TYPE':self.headers['Content-Type'],
                }
            )
            r_file = form.getvalue("file")
            pd.set_option('display.width', 1000)
            pd.set_option('colheader_justify', 'center')
            pd_worklogs=pd.ExcelFile(r_file[1])
            i_timezone = int(form.getvalue("timezone")[0])
            r_projects = form.getvalue("projects").replace(',', ' ').replace(';', ' ').split()
            r_work = form.getvalue("work")
            r_startdate = form.getvalue("startdate")
            r_starttime = form.getvalue("starttime")
            r_enddate = form.getvalue("enddate")
            r_endtime = form.getvalue("endtime")
            config = self.getconfig()
            l_projects = r_projects if bool(r_projects) else config['columns']['jiraprojects']
            s_work = config['columns']['work'] if not r_work else r_work
            s_startdate = config['columns']['startdate'] if not r_startdate else r_startdate
            s_starttime = config['columns']['starttime'] if not r_starttime else r_starttime
            s_enddate = config['columns']['enddate'] if not r_enddate else r_enddate
            s_endtime = config['columns']['endtime'] if not r_endtime else r_endtime
            d_result = {'Issue': [], 'Timespent': [], 'Start date': [], 'Start date utc': [], 'Work': []}
            
            for s_sheet in pd_worklogs.sheet_names:
                try:
                    df_worklogs=pd.read_excel(pd_worklogs, sheet_name=s_sheet)

                except:
                        continue

                for s_project in l_projects:
                    try:
                        l_issues = df_worklogs[s_project].dropna().astype(int).unique()
                    except:
                            l_issues = []
                    for i_issue in l_issues:
                        try:
                            df_events=df_worklogs[df_worklogs[s_project]==i_issue]
                            s_issue = s_project + '-' + str(i_issue)
                            for i in df_events.index:
                                df_event = df_worklogs.iloc[i]
                                s_summary = df_event[s_work]
                                ts_start = df_event[s_startdate]+timedelta(hours=df_event[s_starttime].hour-i_timezone, minutes=df_event[s_starttime].minute)
                                ts_end = df_event[s_enddate]+timedelta(hours=df_event[s_endtime].hour-i_timezone, minutes=df_event[s_endtime].minute)
                                td_timespent = ts_end-ts_start
                                s_timespent = str(td_timespent.seconds//3600)+'h '+str((td_timespent.seconds//60)%60)+'m'
                                dt_start = datetime(ts_start.year, ts_start.month, ts_start.day, ts_start.hour, ts_start.minute)
                                d_result['Issue'].append(s_issue)
                                d_result['Timespent'].append(s_timespent)
                                d_result['Start date'].append(dt_start+timedelta(hours=i_timezone))
                                d_result['Start date utc'].append(dt_start)
                                d_result['Work'].append(s_summary)
                        except Exception:
                            traceback.print_exc()
                            continue
            
            df_result = pd.DataFrame(data = d_result)
            # Response
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(df_result.to_html(classes='worklogs_table', table_id='worklogs_table').encode('utf-8'))
            return

        if self.path == '/upload2jira':
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length)
            data = json.loads(data.decode('utf-8'))

            worklogs = data["worklogs"]
            attrs = {'id': 'worklogs_table'}
            pd.set_option('display.width', 1000)
            pd.set_option('colheader_justify', 'center')
            df_worklogs=pd.read_html(worklogs, attrs=attrs)
            df_worklogs=df_worklogs[0]

            api_token = data["jiratoken"]
            server = data["jiraurl"]

            options = {
                'server': server,
                'headers': {
                     'Authorization': 'Bearer ' + api_token
                }            
            }

            # Jira connetctor initialization
            jira = JIRA(options=options)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            i_df_len = len(df_worklogs.index)
            self.wfile.write(('{} '.format(i_df_len)).encode('utf-8'))

            for index, df_row in df_worklogs.iterrows():
                ts_date = datetime.strptime(df_row['Start date utc'], '%Y-%m-%d %H:%M:%S')-timedelta(hours=0, minutes=0)
                # Write to Jira
                jira.add_worklog(issue = df_row['Issue'], timeSpent = df_row['Timespent'], started = ts_date, comment = df_row['Work'])
                # Chunk response
                self.wfile.write(('{} '.format(index)).encode('utf-8'))

            return

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')
        return

def run():
    print('=================================================================')
    print('Starting server...')
    server_address = ('0.0.0.0', 8081)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Server started!')
    httpd.serve_forever()

run()