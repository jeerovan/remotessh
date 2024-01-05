RemoteSSH
------

Introduction
~~~~~~~~~~~~

RemoteSSH is a Python-based project that enables secure remote access to Unix devices directly within a web browser. This open-source solution leverages Python libraries, including Tornado, WebSockets, Paramiko, asyncio and xterm.js, to create a robust and efficient platform for managing Unix devices remotely.

Features
~~~~~~~~

-  Secure Access: Utilize the SSH protocol to establish secure connections to Unix devices, ensuring data integrity and confidentiality.
-  Web-Based Interface: Access Unix devices through a user-friendly web interface, eliminating the need for complex terminal emulators.
-  Real-Time Interaction: Enjoy real-time interaction with remote devices, including executing commands, viewing responses, and managing multiple devices simultaneously.
-  WebSocket Integration: WebSockets provide low-latency, bidirectional communication, delivering a responsive and interactive user experience.
-  Customizable: Adapt and extend the project to suit your specific needs, from adding authentication and authorization to enhancing functionality.

Preview
~~~~~~~

|Login| |Terminal|

How it works
~~~~~~~~~~~~

::

    +---------+     http     +--------+   websocket  +--------+    ssh    +-----------+
    | browser | <----------> | server | <----------> | device | <-------> | ssh server|
    +---------+   websocket  +--------+   websocket  +--------+    ssh    +-----------+

Requirements
~~~~~~~~~~~~

-  Python 3.8+
-  websockets
-  paramiko
-  tornado

Setup On Remote Device
~~~~~~~~~~~~~~~~~~~~~~

1. Install Python
2. Create python virtual environment, run command ``python3 -m venv remotepy``
3. Install requirements, run command ``remotepy/bin/pip install -r requirements.txt``
4. Run python script ``remotepy/bin/python remote_device_shell_client.py``

Setup On Server
~~~~~~~~~~~~~~~~~~~~~~

1. Create python virtual environment, run command ``python3 -m venv serverpy``
2. Install requirements, run command ``serverpy/bin/pip install -r requirements.txt``
3. Install service or directly run python script ``serverpy/bin/python shell_server.py``


Server options
~~~~~~~~~~~~~~

.. code:: bash

    # start a http server with specified listen address and listen port
    wssh --address='2.2.2.2' --port=8000

    # start a https server, certfile and keyfile must be passed
    wssh --certfile='/path/to/cert.crt' --keyfile='/path/to/cert.key'

    # missing host key policy
    wssh --policy=reject

    # logging level
    wssh --logging=debug

    # log to file
    wssh --log-file-prefix=main.log

    # more options
    wssh --help

Browser console
~~~~~~~~~~~~~~~

.. code:: javascript

    // connect to your ssh server
    wssh.connect(hostname, port, username, password, privatekey, passphrase, totp);

    // pass an object to wssh.connect
    var opts = {
      hostname: 'hostname',
      port: 'port',
      username: 'username',
      password: 'password',
      privatekey: 'the private key text',
      passphrase: 'passphrase',
      totp: 'totp'
    };
    wssh.connect(opts);

    // without an argument, wssh will use the form data to connect
    wssh.connect();

    // set a new encoding for client to use
    wssh.set_encoding(encoding);

    // reset encoding to use the default one
    wssh.reset_encoding();

    // send a command to the server
    wssh.send('ls -l');

Custom Font
~~~~~~~~~~~

To use custom font, put your font file in the directory
``webssh/static/css/fonts/`` and restart the server.

URL Arguments
~~~~~~~~~~~~~

Support passing arguments by url (query or fragment) like following
examples:

Passing form data (password must be encoded in base64, privatekey not
supported)

.. code:: bash

    http://localhost:8888/?hostname=xx&username=yy&password=str_base64_encoded

Passing a terminal background color

.. code:: bash

    http://localhost:8888/#bgcolor=green

Passing a user defined title

.. code:: bash

    http://localhost:8888/?title=my-ssh-server

Passing an encoding

.. code:: bash

    http://localhost:8888/#encoding=gbk

Passing a command executed right after login

.. code:: bash

    http://localhost:8888/?command=pwd

Passing a terminal type

.. code:: bash

    http://localhost:8888/?term=xterm-256color

Use Docker
~~~~~~~~~~

Start up the app

::

    docker-compose up

Tear down the app

::

    docker-compose down

Tests
~~~~~

Requirements

::

    pip install pytest pytest-cov codecov flake8 mock

Use unittest to run all tests

::

    python -m unittest discover tests

Use pytest to run all tests

::

    python -m pytest tests

Deployment
~~~~~~~~~~

Running behind an Nginx server

.. code:: bash

    wssh --address='127.0.0.1' --port=8888 --policy=reject

.. code:: nginx

    # Nginx config example
    location / {
        proxy_pass http://127.0.0.1:8888;
        proxy_http_version 1.1;
        proxy_read_timeout 300;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Real-PORT $remote_port;
    }

Running as a standalone server

.. code:: bash

    wssh --port=8080 --sslport=4433 --certfile='cert.crt' --keyfile='cert.key' --xheaders=False --policy=reject

Tips
~~~~

-  For whatever deployment choice you choose, don't forget to enable
   SSL.
-  By default plain http requests from a public network will be either
   redirected or blocked and being redirected takes precedence over
   being blocked.
-  Try to use reject policy as the missing host key policy along with
   your verified known\_hosts, this will prevent man-in-the-middle
   attacks. The idea is that it checks the system host keys
   file("~/.ssh/known\_hosts") and the application host keys
   file("./known\_hosts") in order, if the ssh server's hostname is not
   found or the key is not matched, the connection will be aborted.

.. |Build Status| image:: https://travis-ci.org/huashengdun/webssh.svg?branch=master
   :target: https://travis-ci.org/huashengdun/webssh
.. |codecov| image:: https://codecov.io/gh/huashengdun/webssh/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/huashengdun/webssh
.. |PyPI - Python Version| image:: https://img.shields.io/pypi/pyversions/webssh.svg
.. |PyPI| image:: https://img.shields.io/pypi/v/webssh.svg
.. |Login| image:: https://github.com/huashengdun/webssh/raw/master/preview/login.png
.. |Terminal| image:: https://github.com/huashengdun/webssh/raw/master/preview/terminal.png

