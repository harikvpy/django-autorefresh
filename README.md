# django-autorefresh
Chrome and Firefox extensions for detecting file change and auto refreshing the 
Django development server webpage.

# Introduction
Django development server has the neat capability of reloading itself whenever 
the project's python source files are saved, ensuring that the latest version 
of the project is served at all times. However, to see the changes in the 
browser, you need manually refresh the relevant page or resort to incorporating 
a Javascript such as [live.js](http://livejs.com/) in our source which will keep 
sending HEAD requests to the server to see if the page has changed and if it has 
reload the page.

The former approach obviously is repetitive and needlessly painful. The latter 
approach works fine, but it results in additional requests to your server, 
something that you may be able to live with or if you're like me, you don't 
appreciate too much.

Django-autorefresh is a solution to address this.

# How it works
It has two components -- a browser extension and a django app. The browser 
extension allows you to activate the auto refresh feature from a toolbar button.
Once activated the extension will keep polling a dedicated server in the Django 
project to see if the page needs to be refreshed. The Django app component 
incorporates this additional dedicated server that provides the requesting 
client with the refresh status.

Whever the project's underlying python sources change and consequently Django 
development server reloads itself, the Django app will monitor this and in the 
subsequent refresh status request from the extension, return a refresh required 
status causing the extension to force reload the activated tab.

Note that this addional server is bound to localhost only and the app does not 
involve any models and/or views. All it has is a single python source for the 
`autorefreshserver` management command. So leaving it in the production code has 
no negative impact.

# How to use
* Install the relevant browser extension. Versions for both Firefox and Chrome 
  are provided. Extensions are also available in the respective extension 
  marketplace. You may also install the extension from its source after 
  cloning the repo locally.
* Install the companion app `django-app/autorefresh` in your python environment.
  You can do this by `pip install -e django-app/setup.py`.
* Run the development server using the command line `python ./manage.py autorefreshserver`.
* Select the Firefox or Chrome tab displaying the Django development server page
* Click on the Auto Refresh toolbar button to activate the auto refresh feature
* Go on and edit your Django project's source files and save them. See the 
  browser page being automatically refreshed. You can specify bind address and
  port for the server just like you would for the `runserver` management 
  command.

# Additional Details
By default the refresh status server is listening on port 32000 (bound to 
localhost). You can change this by specifying `--refreshport <portnumber>` 
along with the `autorefreshserver`. If you change it, make sure you specify the 
same port number in the extension as well by configuring its options.

# Notes
This piece was inspired by the excellent Firefox extension 
[FF-Remote-Control](https://github.com/FF-Remote-Control/FF-Remote-Control). 
I used it for a while, but found the necessity to press an additional key 
(or two in my case as I had a VIM script bound to `<leader>r`) from the editor 
a bit of a pain. Do note that `FF-Remote-Control`, by its design does provide 
the additional capability testing instrumentation as it allows the browser 
refresh to be externally controlled. So it still has a place in your arsenal.

