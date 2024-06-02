#!/usr/bin/python3.10
import pandas as pd
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi, json
from datetime import datetime, timedelta
from jira import JIRA

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        # Cache request
        path = self.path

        # Validate request path, and set type
        if path == "/html/index.html":
            type = "text/html"
        elif path == "/html/style.css":
            type = "text/css"
        elif path == "/html/favicon.ico":
            type = "image/x-icon"
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
        with open(path, 'rb') as file: 
            self.wfile.write(file.read()) # Send

    def do_POST(self):
        if self.path == '/upload':
            form = cgi.FieldStorage(
                fp = self.rfile,
                headers = self.headers,
                environ = {
                    'REQUEST_METHOD':'POST',
                    'CONTENT_TYPE':self.headers['Content-Type'],
                }
            )
            data = form.getvalue("file")
            s_sheet="Лист2"
            pd.set_option('display.width', 1000)
            pd.set_option('colheader_justify', 'center')
            pd_worklogs=pd.ExcelFile(data[1])
            df_worklogs=pd.read_excel(pd_worklogs, sheet_name=s_sheet)
            i_timezone = 3 # Timezone
            l_projects = [ 'VEGA' ]
            d_result = {'Issue': [], 'Timespent': [], 'Date start': [], 'Date start utc': [], 'Theme': []}
            for s_project in l_projects:
                l_issues = df_worklogs[s_project].dropna().unique()
                for i_issue in l_issues:
                    df_events=df_worklogs[df_worklogs[s_project]==i_issue]
                    s_issue = s_project + '-' + str(i_issue)
                    for i in df_events.index:
                        df_event = df_worklogs.iloc[i]
                        s_summary = df_event['Тема']
                        print(df_event['Дата начала'])
                        ts_start = df_event['Дата начала']+timedelta(hours=df_event['Время начала'].hour-i_timezone, minutes=df_event['Время начала'].minute)
                        ts_end = df_event['Дата завершения']+timedelta(hours=df_event['Время завершения'].hour-i_timezone, minutes=df_event['Время завершения'].minute)
                        td_timespent = ts_end-ts_start
                        s_timespent = str(td_timespent.seconds//3600)+'h '+str((td_timespent.seconds//60)%60)+'m'
                        dt_start = datetime(ts_start.year, ts_start.month, ts_start.day, ts_start.hour, ts_start.minute)
                        print(s_issue, s_timespent, dt_start+timedelta(hours=i_timezone), s_summary)
                        d_result['Issue'].append(s_issue)
                        d_result['Timespent'].append(s_timespent)
                        d_result['Date start'].append(dt_start+timedelta(hours=i_timezone))
                        d_result['Date start utc'].append(dt_start)
                        d_result['Theme'].append(s_summary)
            
            df_result = pd.DataFrame(data = d_result)
            # Возвращаем результат клиенту
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(df_result.to_html(classes='worklogs_table', table_id='worklogs_table').encode('utf-8'))
            return

        if self.path == '/upload2jira':
            form = cgi.FieldStorage(
                fp = self.rfile,
                headers = self.headers,
                environ = {
                    'REQUEST_METHOD':'POST',
                    'CONTENT_TYPE':self.headers['Content-Type'],
                }
            )
            data = form.getvalue("worklogs")
            print(data)
            attrs = {'id': 'worklogs_table'}
            pd.set_option('display.width', 1000)
            pd.set_option('colheader_justify', 'center')
            df_worklogs=pd.read_html(data, attrs=attrs)
            df_worklogs=df_worklogs[0]

            i_timezone = 3 # Timezone
            api_token = form.getvalue("jira-token") # Jira API token
            server = form.getvalue("jira-url") # Jira server URL
            print("jira-url: ", server)
            print("jira-token", api_token)

            options = {
                'server': server,
                'headers': {
                     'Authorization': 'Bearer ' + api_token
                }            
            }

            # Инициализация коннектора с jira
            jira = JIRA(options=options)

            for index, df_row in df_worklogs.iterrows():
                print(df_row['Issue'], df_row['Timespent'], df_row['Date start'], df_row['Theme'])
                ts_date = datetime.strptime(df_row['Date start'], '%Y-%m-%d %H:%M:%S')-timedelta(hours=i_timezone, minutes=0)
                #dt_date = datetime(ts_date.year, ts_date.month, ts_date.day, ts_date.hour, ts_date.minute)
                print(df_row['Issue'], df_row['Timespent'], ts_date, df_row['Theme'])
                       
                jira.add_worklog(issue = df_row['Issue'], timeSpent = df_row['Timespent'], started = ts_date, comment = df_row['Theme'])
            
            # Возвращаем результат клиенту
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(bytes("Success!", 'utf-8'))
            return

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')
            return

def run():
    print('Starting server...')
    server_address = ('0.0.0.0', 8081)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Server started!')
    httpd.serve_forever()

run()