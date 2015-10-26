Welcome to the _Django Auto Refresh_ Firefox Extension.

Once activated, it works with the django app 'autorefresh' to automatically refresh
the activated browser window displaying the Django development server page whenever
the Django development server is reloaded.

Getting Started
===============

* Download and install the extension
* Add the companion Django app 'autorefresh' to your Django project's
  app list by adding it to INSTALLED_APPS in settings.py
* Run the Django development server by using ./manage.py autorefreshserver
  instead of using ./manage.py runserver
* Select the Firefox window or tab displaying the Django development server page
* Click the Auto Refresh toolbar button to activate the auto refresh feature
* Go on and edit your Django project's python source files and save them. See
  the browser page being automatically refreshed after the Django development 
  server has reloaded.

Preferences and Controlling Behavior
====================================

There are preferences for:

* Which TCP port number to query to detect for refresh status. 

In addition, by default when firefox is initially started, Django Auto Refresh is
_not_ active. You have to select a window/tab and start Auto Refresh by
clicking the toolbar button.

But it _is_ possible to start Django Auto Refresh automatically when Firefox 
starts by setting the environment `FIREFOX_START_REMOTE_CONTROL=1`. If that
environment variable is set _and_ the icon is present on the toolbar, it will
start when Firefox starts. The requirement for the icon to be present is to
avoid this extension being used for malicious purposes without the user
knowing.

Issues
======
Please report any problems to the
[Issue tracker](https://github.com/harikvpy/django-auto-refresh/issues)

License
=======

Remote Control is licensed under the
[GNU General Public License v2.0](http://www.gnu.org/licenses/gpl-2.0.html)
(See also [gpl-2.0.txt](gpl-2.0.txt))
