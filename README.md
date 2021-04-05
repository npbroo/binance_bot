SETTING UP A NEW PROJECT:
1.) First clone the project
    git clone <url>

2.) Optionally, Set up the virtual environment (recommended)
    Create the venv directory
        python3 -m venv venv

    Activate the virtual environment
        (linux and mac:)
        source venv/bin/activate
        (windows:)
        venv\Scripts\activate 

3.) Install the dependencies
then install the requirements
    pip install -r requirements.txt

    If you get errors installing ta-lib:
    (mac:)
        brew install ta-lib
    (windows:)
        download and install the ta-lib wrapper for your python version and architecture
        then use pip to install

4.) Add you Binance API key
Then add your api key and secret key in the config file


RESOURCES:
Binance API:
https://github.com/binance-us/binance-official-api-docs
