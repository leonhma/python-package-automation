This is a template that contains workflows to automatically update documentation using sphinx, push it to github pages, upload release binaries as assets and run existing unittests on every push.

# How to use this template

## Setup

* First, think of a name for your package. Make shure it's not yet taken on pypi and testpypi.
* Second, click 'use this template' in the upper right corner
* Name your repository the name you have just thought of (dashes will be replaced with underscores) and choose a license and description for it. This will enable the setup workflow to automatically fill in some of the details.
* Next, in your newly created repository, go to the actions tab, select 'setup' and click on 'run workflow'
* Select your main branch and click 'run workflow'
* You should now see a job 'setup' pop up (after ca. 10 sec, you might have to refresh the page). Wait for it to finish and move on.

**Feel free to now edit setup.py, docs/*, readme.md and the folder named like your repo to your liking**

## Automated distribution on release

* Sign up for an account at testpypi and pypi
* Under account settings (in your pypi account) select API tokens and create a new one with the **permission to upload to the entire account**.
* Go to the settings page in your repo and select secrets, click 'add secret' and paste your token from testpypi into a secret named 'TEST_PYPI_PASSWD' and the one from pypi to 'PYPI_PASSWD'.
* You are now able to create a release. Choose a tag name that contains only alphanumericals, underscores and dots. If you select 'This is a prerelease', your package will only be uploaded to testpypi, if you don't, it will be uploaded to both testpypi and pypi.

## GitHub pages

> Not advised you use this. Use readthedocs.io. It contains a small amount of ads, but has more features. Just delete the `gh-pages.yml` workflow if you don't want to use it.

* If this was your first release, go to the settings tab and scroll down to the github pages section. Select gh-pages as the branch to host your docs (it has just been created in the release workflow) and choose root as the directory containing your docs.
* You should now see github-pages under the environments in the sidebar. Click on it and select 'View deployment' this will take you to your ready-made website. If it says 404, just give it 2 minutes and retry.

## Automatic unittesting

* If you're familiar with the python testing framework unittests, this is for you.
* Write you test like you normally would. With every push, your tests are run against the code you wrote. If your project depends on libraries, you can add a `requirements.txt` file, or just let `setup.py` do it's thing.
