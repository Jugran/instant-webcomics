# Instant Webcomics
A simple program written in python3 which downloads and shows comic strips from all your favorite sources.
- - - - 

### Dependencies 
Instant Webcomics requires PyGObject for GTK interface, BeautifulSoup4 and lxml for html/xml parsing, and requests for sending and recieving http requests.

Guide for installing PyGOject is available in [PyGOject's official documentation](https://pygobject.readthedocs.io/en/latest/getting_started.html) for diffrent platforms.

Rest of the packages are available on PyPI.
```
    pip install bs4 requests lxml
```

## Installation
Before proceding make sure that all the required dependencies are installed.

#### GNU/Linux

1. Clone the git repo
    ```
    git clone https://github.com/Jugran/instant-webcomics
    cd instant-webcomics/instant-webcomics
    ```
2. Make file executable
    ```
    chmod +x instant-webcomics.py
    ```
3. Run the script
    ```
    ./instant-webcomics.py
    ```
### Uninstallation
Simply remove the directory
    ```
    rm -rf instant-webcomics
    ```


