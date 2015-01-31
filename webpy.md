Install
-------

sudo easy_install web.py
sudo easy_install tabulate
sudo easy_install python-itunes
sudo pip install musicbrainzngs



Web.py hello world
------------------

```
import web
        
urls = (
    '/(.*)', 'hello'
)
app = web.application(urls, globals())

class hello:
    def GET(self, name):
        if not name: 
            name = 'World'
        return 'Hello, ' + name + '!'

if __name__ == "__main__":
    app.run()
```

Apache:
=======

http://webpy.org/cookbook/mod_wsgi-apache

```
 WSGIScriptAlias /appname /var/www/webpy-app/code.py/
 AddType text/html .py
```

For pub:
https://ubuntuincident.wordpress.com/2012/05/06/use-python-like-php-in-public_html-with-wsgi/
http://blog.dscpl.com.au/2012/10/why-are-you-using-embedded-mode-of.html

Need --> WSGIRestrictEmbedded On
and
```
WSGIDaemonProcess [user name] user=[user name] home=/home/[user name]/public_html
<Directory /home/[user name]/public_html>
    WSGIProcessGroup [user name]
</Directory>
```
and in sites default
```
AddHandler wsgi-script .wsgi
```
Templates
---------

http://webpy.org/docs/0.3/templetor
http://www.artima.com/weblogs/viewpost.jsp?thread=335549



Remember to map the status directory! and do all css/js relative to that
AliasMatch ^/~(.*)/[^/]+\.wsgi/static/(.*) /home/$1/static/$2


http://codeimpossible.com/2010/01/13/solving-document-ready-is-not-a-function-and-other-problems/
