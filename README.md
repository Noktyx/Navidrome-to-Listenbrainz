# Navidrome-to-Listenbrainz
A simple CLI tool, made in Python, to help you import your listening history and your favourites (liked tracks) from Navidrome to ListenBrainz.

## Requirements

- Python >= 3.10
- The `requests` Python library

---

## Setup


### 0. Locate your Navidrome database file

Navidrome stores everything in a SQLite database called `navidrome.db`, kept in a folder specified in your Navidrome configuration file (`navidrome.toml`).

If you don't remember where `navidrome.db` is located, you must find your **configuration file**. You can find your **configuration file** in your Navidrome web interface following these steps:

1. Click the **Settings** icon
![Top-right of the screen](media_for_readme/step_1.webp)

2. Click **About**
![The 'About' button on the pop-up](media_for_readme/step_2.webp)

3. And, finally, Click **Configuration**
![](media_for_readme/step_3.webp)


The filepath of your **configuration file** (Typically named `navidrome.toml`) is shown in the first row under the *'Current Value'* column. Once you have that path, enter the **configuration file** and look for the `DataFolder` variable; that should contain the path of the folder where `navidrome.db` resides. Navigate to that folder and there you should be finally able to find `navidrome.db`. Please note that `navidrome.db-wal`, `navidrome.db-shm` or any of the sorts are not to be confused with `navidrome.db`, as those are unrelated SQLite's temporary files.


### 1. Copy your Navidrome database here

Now that you've found your `navidrome.db`, copy it into this project. Place it inside the `resources/` folder located inside the project's folder (If the folder doesn't exist, create it):

```
Navidrome-to-Listenbrainz/
├── resources/
│   └── navidrome.db    <-- Here
├── utils/
├── main.py
├── config.json
├── requirements.txt
...
```

Or just put it wherever you want and update the path in the `db_path` key from `config.json` to reflect that.


### 2. Get your ListenBrainz token

Go to your [ListenBrainz profile settings](https://listenbrainz.org/profile/) and copy your user token, or keep it for later. The tool requires it in order to function; it is requestes during the execution of the tool.


### 3. Run it

Open a console inside the project's folder and, depending on the setup, run
```bash
python main.py
```
or
```bash
python3 main.py
```

And you should be done! The script will walk you through the rest interactively and hopefully help you.

However, on the occasion that this outputs any error, using the console open in the project's folder, *run the following commands* (Which are slightly different based on your operating system):

On **Mac/Linux/FreeBSD:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

On **Windows:**
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
(Assuming you're using the *Command Prompt (CMD)*; if you are using *PowerShell (PS)*, then you must run `venv\Scripts\Activate.ps1` as opposed to `venv\Scripts\activate`.)

If this works, next time you'll want to run the program you'll only need to activate the `venv` again and run `main.py`, as such:

On **Mac/Linux/FreeBSD:**
```bash
source .venv/bin/activate
python3 main.py
```

On **Windows:**

In the *Command Prompt (CMD)*:
```bat
.venv\Scripts\activate
python main.py
```
In *PowerShell (PS)*:
```powershell
.venv\Scripts\Activate.ps1
python main.py
```

If you are still running into issues (Sad :[ ), make sure you have **Python 3.10** or **higher** installed on your system.

---

Please note that ListenBrainz may take some time to display newly imported data. If the import completed successfully, please be patient and allow anywhere from a few minutes to an hour for the changes to appear in your ListenBrainz profile.

---

## Configuration

All settings live in `config.json`:

|Key|Default|Description|
|-----|---------|-------------|
|`db_path`|`resources/navidrome.db`|Path to the Navidrome database file|
|`listenbrainz_submit_url`|*([ListenBrainz API](https://api.listenbrainz.org/1/submit-listens))*|Endpoint to submit listens (scrobbles) to|
|`listenbrainz_feedback_url`|*([ListenBrainz API](https://api.listenbrainz.org/1/feedback/recording-feedback))*|Endpoint to submit feedbacks (favourites) to|
|`listenbrainz_validate_url`|*([ListenBrainz API](https://api.listenbrainz.org/1/validate-token))*|Endpoint to validate a token|
|`max_submit_attempts`|`3`|Maximum number of attempts before aborting a batch or feedback|
|`seconds_before_reattempt`|`2`|How long to wait (in seconds) before retrying to submit a failed batch or feedback|

The path to the **configuration file** can only be changed by directly modifying the default value of the `config_path` parameter in the `load_config` function, located in `main.py`.

---