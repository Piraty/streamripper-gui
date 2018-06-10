#!/usr/bin/python

try:
        import sys
        import os
        import os.path
        import locale
        import gettext
        import pygtk
        pygtk.require("2.0")
        import gtk
        import gtk.glade
        import pango
        import gobject
        import re
        import urllib
        import dbus
        import subprocess
        import signal
        import shlex
except:
        print "Please install all dependencies!"
        sys.exit(1)

APP = "streamripper-gui"
DIR = "/usr/share/locale"
APP_VERSION = "0.1.2"

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

LOCALE = locale.getlocale()[0]
# print gettext.find(APP) 


class appgui:
        def __init__(self):
                self.pathname = os.path.dirname(sys.argv[0])
                self.abspath = os.path.abspath(self.pathname)
                self.gladefile = self.abspath + "/streamripper-gui.glade"
                self.window1 = gtk.glade.XML(self.gladefile,"window1",APP)
                self.record_active = False

                dic = {
                        "on_button1_clicked": self.on_button1_clicked,
                        "on_button2_clicked": self.on_button2_clicked,
                        "on_button4_clicked": self.about,
                        "on_button5_clicked": self.on_button5_clicked,
                        "on_window1_delete_event" : self.quit#(gtk.main_quit)
                }
                
                self.window1.signal_autoconnect (dic)
                
                
                self.statusIcon = gtk.status_icon_new_from_icon_name('audio-x-generic')
                self.statusIcon.connect("activate", self.toggleMainWindow)
                
                #while gtk.events_pending():
                        #gtk.main_iteration_do()
                meta = self.getPlayerStream()
                if meta:
                        stream = self.ProcessLocation(meta['location'])
                        self.window1.get_widget('entry1').set_text(stream)
                
                
                
        def toggleMainWindow(self, widget, data = None):
                self.window1.get_widget("window1").set_visible(not self.window1.get_widget("window1").get_visible())
        
        def ProcessLocation(self, location):
                m = re.search('^di://([a-zA-Z]+)$', location)
                if m:
                        url = 'http://listen.di.fm/public3/%s.pls' % m.group(1)
                        try:
                                data = urllib.urlopen(url).read()
                                m1 = re.search('^File\d+=(.*?)$', data, re.MULTILINE)
                                if m1:
                                        return m1.group(1)
                                else:
                                        return ''
                        except:
                                return ''
                else:
                        return location
                
        def getPlayerStream(self):
                bus = dbus.SessionBus()
                interfaces = [
                        'org.mpris.clementine',
                        'org.mpris.MediaPlayer2.clementine',
                        'org.mpris.banshee',
                        'org.mpris.MediaPlayer2.banshee',
                        'org.mpris.rhythmbox',
                        'org.mpris.MediaPlayer2.rhythmbox',
                        'org.mpris.audacious',
                        'org.mpris.MediaPlayer2.audacious',
                        'org.mpris.amarok',
                        'org.mpris.MediaPlayer2.amarok',
                        'org.mpris.MediaPlayer2.bmp',
                        'org.mpris.MediaPlayer2.xmms2',
                        'org.mpris.radiotray',
                        #'org.mpris.MediaPlayer2.vlc',
                ]
                
                for interface in interfaces:
                        try:
                                player = bus.get_object(interface, '/Player')
                                return player.GetMetadata()
                        except:
                                pass
                
        def on_button2_clicked(self, widget, data = None):
                url = self.window1.get_widget('entry1').get_text()
                m = re.search('\.(pls|m3u)$', url)
                if m:
                        if m.group(1) == 'pls':
                                try:
                                        data = urllib.urlopen(url).read()
                                        m1 = re.search('^File\d+=(.*?)$', data, re.MULTILINE)
                                        if m1:
                                                stream = m1.group(1).strip()
                                                self.window1.get_widget('entry1').set_text(stream)
                                        else:
                                                stream = ''
                                except:
                                        stream = ''
                        elif m.group(1) == 'm3u':
                                try:
                                        data = urllib.urlopen(url).read()
                                        m1 = re.search('^(http://.*)$', data, re.MULTILINE)
                                        if m1:
                                                stream = m1.group(1).strip()
                                                self.window1.get_widget('entry1').set_text(stream)
                                        else:
                                                stream = ''
                                except:
                                        stream = ''
                                
                else:
                        stream = url
                if stream:
                        dest_dir = self.window1.get_widget('filechooserbutton1').get_current_folder()
                        self.ns = Namespace()
                        self.record_active = True
                        self.window1.get_widget("button2").hide()
                        self.window1.get_widget("button3").show()
                        self.window1.get_widget("label3").show()
                
                
                        #self.window1.get_widget("progressbar1").set_text(_('Starting...'))
                        def cancel_process(widget, other = None):
                                print "KILLING"
                                self.ns.kill_process = True
                                return False
                        
                        self.window1.get_widget("button3").connect("clicked",(cancel_process))

                        while gtk.events_pending():
                                gtk.main_iteration_do()

                        cmd = 'streamripper "%s" -m 30 -t -d "%s"' % (stream, dest_dir)

                        print cmd
                        argv =  shlex.split(cmd)

                        self.ns.process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=None)
                        #self.ns.process = subprocess.Popen(argv, stdout=None, stderr=None, startupinfo=None)
                        self.ns.kill_process = False

                        
                        while self.ns.process.poll() == None:
                                if self.ns.kill_process:
                                        os.kill(self.ns.process.pid, signal.SIGKILL)
                                        self.ns.process.wait()
                                        try:
                                                self.window1.get_widget("button2").show()
                                                self.window1.get_widget("button3").hide()
                                                self.window1.get_widget("label3").hide()
                                        except:
                                                pass
                                        self.record_active = False
                                        returncode = self.ns.process.returncode
                                        self.ns = None
                                        return returncode
                                else:
                                        line = self.ns.process.asyncread(0.1)
                                        try:
                                                m = re.search('\[(.*?)\](.*?)\[(.*?)\]',line, re.MULTILINE)
                                                if m:
                                                        self.window1.get_widget("label3").set_text(m.group(0))
                                                #self.window1.get_widget("progressbar1").pulse()
                                        except:
                                                pass
                                        while gtk.events_pending():
                                                gtk.main_iteration_do()
                        try:
                                self.window1.get_widget("button2").show()
                                self.window1.get_widget("button3").hide()
                                self.window1.get_widget("label3").hide()
                                pass
                        except:
                                pass  
                                
                                
                        
                        self.record_active = False
                        returncode = self.ns.process.returncode
                        self.ns = None
                        return returncode
                else:
                        self.msg_error(_('Error while processing stream address!'))
                
        def on_button1_clicked(self, widget, data = None):
                meta = self.getPlayerStream()
                if meta:
                        stream = self.ProcessLocation(meta['location'])
                        self.window1.get_widget('entry1').set_text(stream)

        def on_button5_clicked(self, widget, data = None):
                self.window1.get_widget("window1").set_visible(False)
        
        def quit(self, widget, data = None):
                if self.record_active:
                        self.window1.get_widget("button3").clicked()
                
                gtk.main_quit()
                #sys.exit(0)
   
                        
        def about(self, widget, data = None):
                # show about dialog
                about = gtk.AboutDialog()
                about.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
                about.set_program_name(_("Streamripper GUI"))
                about.set_version(APP_VERSION)
                about.set_authors([_("Krasimir S. Stefanov <lokiisyourmaster@gmail.com>")])
                about.set_website("http://skss.learnfree.eu/")
                about.set_translator_credits(_("Bulgarian - Krasimir S. Stefanov <lokiisyourmaster@gmail.com>"))
                
                #pixbuf = gtk.gdk.pixbuf_new_from_file('streamripper-gui.svg')
                #about.set_logo(pixbuf)
                license = _('''Streamripper GUI
Copyright (C) 2012 Krasimir S. Stefanov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.''')
                about.set_license(license)
                about.run()
                about.hide()

        def msg_info(self, msg):
                        dialog = gtk.MessageDialog(self.window1.get_widget("window1"),gtk.DIALOG_MODAL,gtk.MESSAGE_INFO,gtk.BUTTONS_OK)
                        dialog.set_markup(msg)
                        dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
                        dialog.run()
                        dialog.destroy()
                        
        def msg_error(self, msg):
                        dialog = gtk.MessageDialog(self.window1.get_widget("window1"),gtk.DIALOG_MODAL,gtk.MESSAGE_ERROR,gtk.BUTTONS_OK)
                        dialog.set_markup(msg)
                        dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
                        dialog.run()
                        dialog.destroy()

class Namespace: pass

if __name__ == '__main__':
                app = appgui()
                gtk.main()


        
