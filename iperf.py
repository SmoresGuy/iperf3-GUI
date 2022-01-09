#!/usr/bin/env python
'''
GUI for Iperf3
see https://iperf.fr/iperf-servers.php for details of list of servers given
N Waterton V 1.0 19th April 2018: initial release
N Waterton V 1.1 26th April 2018: Added geographic data
N Waterton V 1.2 4th May 2018: Added Yandex maps service due to impending google API key requirement.

Onemarcfifty 2022-01-09:    removed internet functions, 
                            local op only
                            removed ping
Onemarcfifty 2022-01-09: continuous server operation

'''

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__VERSION__ = __version__ = '1.1'

import subprocess, sys, os, tempfile
from platform import system as system_name  # Returns the system/OS name
import time
import configparser
#import math
#import json
#import urllib2
import tkinter as tk
from tkinter import ttk
import meter as m
import re
import base64

class Mainframe(tk.Frame):
    
    def __init__(self,master, arg=None, *args,**kwargs):
        #super(Mainframe,self).__init__(master,*args,**kwargs)
        tk.Frame.__init__(self, master, *args,**kwargs)
        
        self.ip_address = None # ip address of current remote server
        self.arg = arg
        self.master = master
        self.ip_info = {}
        self.meter_size = 300 #meter is square
        self.no_response = 'No Response from iperf3 Server'
        self.server_list = ['iperf.he.net',
                            'bouygues.iperf.fr',
                            'ping.online.net',
                            'ping-90ms.online.net',
                            'iperf.eenet.ee',
                            'iperf.volia.net',
                            'iperf.it-north.net',
                            'iperf.biznetnetworks.com',
                            #speedtest.wtnet.de,
                            'iperf.scottlinux.com']
        self.server_list[0:0] = self.arg.ip_address
        self.port_list   = ['5200',
                            '5201',
                            '5202',
                            '5203',
                            '5204',
                            '5205',
                            '5206',
                            '5207',
                            '5208',
                            '5209']
        self.max_options = ['OFF', 'Track Needle', 'Hold Peak']     
        self.max_range = 1000
        self.min_range = 10
        self.resolution = 10
        #self.ranges = list(range(self.min_range, self.max_range+self.resolution, self.resolution))
        self.ranges = [10,30,50,100,200,400,600,800,1000]
        self.duration = tk.Variable()
        self.threads = tk.Variable()
        self.server = tk.Variable()
        #self.server.trace('w', self.servercalback)
        self.server_port = tk.Variable()
        self.range = tk.Variable()
        self.reset_range = tk.Variable()
        self.threads.set('16')
        self.reset_range.set(self.arg.reset_range) 

#        self.read_config_file() #load data if config file exists
        self.msg_label = tk.Label(self, text="Pong:")
        self.msg_label.grid(row=0, sticky=tk.E)
#        self.ping_label = tk.Label(self, anchor='w', width=60)
#        self.ping_label.grid(row=0, column=1, columnspan=3, sticky=tk.W)
        
        tk.Label(self, text="Download:").grid(row=2, sticky=tk.E)
        self.download_label = tk.Label(self, anchor='w', width=60)
        self.download_label.grid(row=2, column=1, columnspan=3, sticky=tk.W)
        
        tk.Label(self, text="Upload:").grid(row=3, sticky=tk.E)
        self.upload_label = tk.Label(self, anchor='w', width=60)
        self.upload_label.grid(row=3, column=1, columnspan=3, sticky=tk.W)
        
        self.meter = m.Meter(self,height = self.meter_size,width = self.meter_size)
        self.range.trace('w',self.updaterange)  #update range when value changes
        self.range.set(self.arg.range)
        self.meter.set(0)
        self.meter.grid(row=5, column=0, columnspan=4)
 
        tk.Label(self, text="Server:").grid(row=6, sticky=tk.E)
        self.ipaddress= ttk.Combobox(self, textvariable=self.server, values=self.server_list, width=39)
        self.ipaddress.current(0)
        self.ipaddress.bind("<<ComboboxSelected>>", self.servercalback)
        self.ipaddress.grid(row=6, column=1, columnspan=2, sticky=tk.W)
        self.servercalback()    #update current displayed map (if enabled)
        
        self.port= ttk.Combobox(self, textvariable=self.server_port, values=self.port_list, width=4)
        if self.arg.port in self.port_list:
            self.port.current(self.port_list.index(self.arg.port))
        else:
            self.port_list.insert(0,self.arg.port)
            self.port.config(values=self.port_list, width=len(self.arg.port))
            self.port.current(0)
        self.port.grid(row=6, column=3, sticky=tk.W)
        
        tk.Label(self, text="Progress:").grid(row=7, sticky=tk.E)
        self.progress_bar = ttk.Progressbar(self
        ,orient="horizontal"
        ,length=325
        , mode="determinate")
        self.progress_bar.grid(row=7, column=1, columnspan=3, sticky=tk.W)
        
        tk.Label(self, text="Peak Mode:").grid(row=8, sticky=tk.E)
        self.max_mode_value = tk.StringVar()
        try:
            self.max_mode_value.set(self.max_options[arg.max_mode_index])
        except ValueError:
            self.max_mode_value.set(self.max_options[0]) # default value
        self.max_mode = tk.OptionMenu(self
         ,self.max_mode_value
         ,*self.max_options)
        self.max_mode.grid(row=8, column=1, columnspan=2, sticky=tk.W)

        self.reset_range_box = tk.Checkbutton(self, text="Reset Range for Upload", variable=self.reset_range)
        self.reset_range_box.grid(row=8, column=2, sticky=tk.W)

        tk.Label(self, text="Range:").grid(row=9, sticky=tk.W)
        self.range_box = ttk.Combobox(self, textvariable=self.range, values=self.ranges, width=4)
        self.range_box.grid(row=10, column=0, rowspan=2)
        
        self.duration_scale = tk.Scale(self,width = 15 ,from_ = 10, to = 30
        ,orient = tk.HORIZONTAL
        ,label='Test Duration'
        ,variable=self.duration)
        self.duration_scale.grid(row=9, column=1, rowspan=2)
        
        self.threads_scale = tk.Scale(self,width = 15 ,from_ = 1, to = 30
        ,orient = tk.HORIZONTAL
        ,label='Threads'
        ,variable=self.threads)
        self.threads_scale.grid(row=9, column=2, rowspan=2)

        self.start_button = tk.Button(self,text = 'Start',width = 15,command = self.run_iperf)
        self.start_button.grid(row=9, column=3)
        self.quit = tk.Button(self,text = 'Quit',width = 15,command = self.quit)
        self.quit.grid(row=10, column=3)
        
    def quit(self):
        print("Exit Program")
        self.done = True
        try:
            self.p.terminate()
            time.sleep(1)
        except AttributeError:
            pass
        
        self.master.destroy()
        sys.exit(0)
        
    def set_control_state(self, state):
        self.ipaddress.config(state=state)
        self.port.config(state=state)
        self.max_mode.config(state=state)
        self.reset_range_box.config(state=state)
        self.range_box.config(state=state)
        self.duration_scale.config(state=state)
        self.threads_scale.config(state=state)
        self.start_button.config(state=state)
        self.update_idletasks()
                    
    def is_ip_private(self,ip):
        # https://en.wikipedia.org/wiki/Private_network

        priv_lo = re.compile("^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        priv_24 = re.compile("^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        priv_20 = re.compile("^192\.168\.\d{1,3}.\d{1,3}$")
        priv_16 = re.compile("^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$")

        res = priv_lo.match(ip) or priv_24.match(ip) or priv_20.match(ip) or priv_16.match(ip)
        return res is not None
        
    
    def show_message(self, message, error=False):
        if error:
            self.msg_label.config(text='Error:')
        else:
            self.msg_label.config(text='')
#        self.ping_label.config(text=message)
        self.update_idletasks()
        
        
    def run_iperf(self):
        if self.server.get() == self.no_response:
            self.show_message('Please select/enter a vaild iperf3 server', True)
            self.update_idletasks()
            return
        self.map = None
        self.show_message('Testing', False)
        self.download_label.config(text='', width=60)
        self.upload_label.config(text='', width=60)
        self.meter.draw_bezel() #reset bezel to default
        self.set_control_state('disabled')
        self.update_idletasks()
        
#        result, message, ip_address = self.ping(self.server.get())
#        if not result:
#            self.show_message('Could not ping server: %s' % self.server.get(), True)
#            self.set_control_state('normal')
#            return
#        self.show_message(message)
        self.update_idletasks()
        
        if len(self.run_iperf3(upload=False)) != 0 and not self.done: #if we get some results (not an error)
            if int(self.reset_range.get()) == 1:
                self.range.set(self.arg.range)  #reset range to default
            self.run_iperf3(upload=True)
            if self.server.get() not in self.server_list:
                self.server_list.append(self.server.get())
                self.ipaddress.config(values=self.server_list)
            try:
                if not self.ip_info[self.ip_address].get('saved', False):
                    self.write_config_file()
            except KeyError:
                pass
        else:
            if self.server.get() not in self.server_list:
                self.server.set(self.no_response)
        self.set_control_state('normal')
        self.update_idletasks()
        
    def run_iperf3(self, upload=False):
        self.done = False
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = int(self.duration.get())
        self.meter.max_val = 0
        self.meter.set(0)
        self.meter.show_max = self.max_options.index(self.max_mode_value.get()) #get index of item selected in max options
        fname = tempfile.NamedTemporaryFile()
        if system_name().lower()=='windows':
            iperf_command = '%s -c %s -p %s -P %s -O 1 -t %s %s --logfile %s' % (self.arg.iperf_exec,
                                                                                self.server.get(), 
                                                                                self.server_port.get(),
                                                                                self.threads.get(),
                                                                                self.duration.get(),
                                                                                '' if upload else '-R',
                                                                                fname.name)
        else:
         if self.arg.server:
            iperf_command = '%s -s -p %s --forceflush' % (self.arg.iperf_exec,
                                                  self.server_port.get())
         else:
            iperf_command = '%s -c %s -p %s -P %s -O 1 -t %s %s '         % (self.arg.iperf_exec,
                                                                                self.server.get(), 
                                                                                self.server_port.get(),
                                                                                self.threads.get(),
                                                                                self.duration.get(),
                                                                                '' if upload else '-R')
        
        self.print("command: %s" % iperf_command)
        message = 'Attempting connection - Please Wait'
        if upload:
            self.upload_label.config(text=message)
        else:
            self.download_label.config(text=message)   
        self.update_idletasks()
        try:
            self.p = subprocess.Popen(iperf_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,bufsize=1)
        except Exception as e:
            self.msg_label.config(text='%s:' % sys.exc_info()[0].__name__)
#            self.ping_label.config(text='(%s) %s' % (self.arg.iperf_exec,e))
            print('Error in command: %s\r\n%s' % (iperf_command,e))
            return []
         
        message = 'Testing'
        if upload:
            self.upload_label.config(text=message)
        else:
            self.download_label.config(text=message)   

        with fname:
            results_list = self.progress(fname if system_name().lower()=='windows' else self.p.stdout, upload)
            
        try:
            self.p.terminate()
            self.setmeter(0)
            self.update_idletasks()
        except (tk.TclError, AttributeError):
            pass
        self.print('End of Test')
        return results_list
        
    def progress(self,capture, upload):
        results_list = []
        units='bits/s'
        total = 0
        while not self.done:
            try:
                line = str(capture.readline() )
                if self.arg.verbose and line: self.print(line.strip())
                if 'Done' in line:
                    break
                if 'Connecting' in line:
                    continue
                if 'error' in line:
                    self.print("%s" % line)
                    self.show_message(line.strip(), True)
                    try:
                        message = 'Max = %s, Avg = %s %s' % (max(results_list), total if total != 0 else sum(results_list) / max(len(results_list), 1), units)
                    except ValueError:
                        message = ''
                    if upload:
                        self.upload_label.config(text=message)
                    else:
                        self.download_label.config(text=message)
                    break
                else:
#                    if (int(self.threads.get()) > 1 and line.startswith('[SUM]')) or (int(self.threads.get()) == 1 and 'bits/sec' in line):
                    if (int(self.threads.get()) > 1 and '[SUM]' in line) or (int(self.threads.get()) == 1 and 'bits/sec' in line):
                        self.progress_bar["value"] += 1
                        speed = float(line.replace('[ ','[').replace('[ ','[').split()[5])
                        units = line.replace('[ ','[').replace('[ ','[').split()[6]
                        if 'receiver' in line:
                            total = speed
                            self.print("Total: %s %s" % (total, units))
                            message = 'Max = %s, Avg = %s %s' % (max(results_list), total, units)
                            if upload:
                                self.upload_label.config(text=message)
                            else:
                                self.download_label.config(text=message)
                            results_list.append(total)
                        else:
                            self.print("Speed: %s %s" % (speed, units))
                            #update range if value is too high
                            if speed > self.meter.range+(self.meter.range/20):  #if more than 5% over-range
                                self.setrange(next((i for  i in self.ranges if i>=speed),self.ranges[-1]))  #increase range if possible
                            self.setmeter(speed)
                            self.setunits(units)
                            self.quit.update()
                            self.update_idletasks()
                        results_list.append(speed)
            except tk.TclError:
                break
        capture.close()
        return results_list
        
    def print(self, str):
        if self.arg.debug:
            print(str)
            
        
    def servercalback(self, *args):
        #server selection changed
        #if self.local_ip == '': return
        self.print('Server has changed to: %s' % self.server.get())
        self.show_message('')
        self.download_label.config(text='')
        self.upload_label.config(text='')
#        self.geography_label.config(text='')
        self.meter.max_val = 0
#        server_name = self.local_ip if self.is_ip_private(self.server.get()) else self.server.get()
#        for k in self.ip_info.keys(): 
#            self.print('checking ip address: %s, server name: %s target: %s' % (k, self.ip_info[k].get('server', None), server_name))
#            if server_name == self.ip_info[k].get('server', None):
#                self.print('FOUND! ip address: %s' % k)
#                self.ip_address = k
#                return
        #no map yet
        self.map = None
        self.update_idletasks()
            
    def updaterange(self, *args):
        self.setrange(self.range.get())
        
    def setrange(self, value):
        self.range.set(value)
        try:
            self.meter.setrange(0,int(value))
        except ValueError:
            self.meter.setrange(0,self.ranges[0])
        
    def setunits(self,value):
        self.meter.units(value)
        
    def setmeter(self,value):
        value = int(value)
        #self.meter.set(value, True)
        self.meter.smooth_set(value, True)
        
class App(tk.Tk):
    def __init__(self, arg):
        #super(App,self).__init__()
        tk.Tk.__init__(self)
        self.title('Iperf3 Network Speed Meter (V %s)' % __VERSION__)
        Mainframe(self, arg=arg).grid()
        
def global_imports(modulename,shortname = None, asfunction = False):
    if shortname is None: 
        shortname = modulename
    if asfunction is False:
        globals()[shortname] = __import__(modulename)
    else:        
        globals()[shortname] = eval(modulename + "." + shortname)

def main():
    import argparse
    max_mode_choices = ['OFF', 'Track', 'Peak']
    parser = argparse.ArgumentParser(description='Iperf3 GUI Network Speed Tester')
    parser.add_argument('-I','--iperf_exec', action="store", default='iperf3', help='location and name of iperf3 executable (default=%(default)s)')
    parser.add_argument('-ip','--ip_address', action="store", nargs='*', default=['192.168.139.143'], help='default server address(\'s) can be a list (default=%(default)s)')
    parser.add_argument('-p','--port', action="store", default='5201', help='server port (default=%(default)s)')
    parser.add_argument('-r','--range', action="store", type=int, default=10, help='range to start with in Mbps (default=%(default)s)')
    parser.add_argument('-R','--reset_range', action='store_false', help='Reset range to Default for Upload test (default = %(default)s)', default = True)
    parser.add_argument('-m','--max_mode', action='store', choices=max_mode_choices, help='Show Peak Mode (default = %(default)s)', default = max_mode_choices[2])
    parser.add_argument('-D','--debug', action='store_true', help='debug mode', default = False)
    parser.add_argument('-S','--server', action='store_true', help='run iperf in server mode', default = False)
    parser.add_argument('-V','--verbose', action='store_true', help='print everything', default = False)
    parser.add_argument('-v','--version', action='version',version='%(prog)s {version}'.format(version=__VERSION__))

    arg = parser.parse_args()
    if arg.verbose: arg.debug=True
    arg.max_mode_index = max_mode_choices.index(arg.max_mode)
    
    App(arg).mainloop()

    
if __name__ == "__main__":
    main()