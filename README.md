# python-package-automation

This is a template that contains workflows to automatically update documentation using sphinx, push it to github pages, upload release binaries as assets and run existing unittests on every push.

## How to use this template

### Setup

* First, think of a name for your package. Make sure it's not yet taken on pypi and testpypi.
* Second, click 'use this template' in the upper right corner
* Name your repository the name you have just thought of (I discourage the use of dashes here, since it can be quite annoying if your package is called differently on pypi and in the program) and set a description. This will enable the setup workflow to automatically fill in some of the details in the package files.
* You should now see a job 'setup' pop up (after ca. 10 sec, you might have to refresh the page). Wait for it to finish and move on.
* You should now as the last step create a license. Create a file called `LICENSE` in the root directory and simply choose one that fits your project.

## Automated distribution on release

* Sign up for an account at testpypi and pypi
* Under account settings (in your pypi account) select API tokens and create a new one with the **permission to upload to the entire account**.
* Go to the settings page in your repo and select secrets, click 'add secret' and paste your token from testpypi into a secret named 'TEST_PYPI_PASSWD' and the one from pypi to 'PYPI_PASSWD'.
* You are now able to create a release. Choose a tag name that contains only alphanumericals, underscores and dots. If you select 'This is a prerelease', your package will only be uploaded to testpypi, if you don't, it will be uploaded to both testpypi and pypi.

## GitHub pages / ReadTheDocs

If you want to host your documentation on ReadTheDocs, everything is already set up for you. Just go to [readthedocs.org](readthedocs.org), create a new project, and fill in some details. (Pro tip: Link your GitHub with RTD and choose to generate previews for pull-requests. You'll see :) )

If you for whatever reason decide to host the documentation on github pages, here are the steps for enabling a documentation build on release:

* Move `docs/opt/gh-pages.yml` into `.github/workflow/gh-pages.yml`
* Create a release
* If this was your first release, go to the settings tab and scroll down to the github pages section. Select gh-pages as the branch to host your docs (it has just been created in the release workflow) and choose root as the directory containing your docs.
* You should now see github-pages under the environments in the sidebar. Click on it and select 'View deployment' this will take you to your ready-made website. If it says 404, just give it 2 minutes and retry.

## Automatic unittesting

* If you're familiar with the python testing framework `unittest`, this is for you.
* Write your test like you normally would. With every push, your tests are run against the code you wrote. If your project depends on libraries, you can add a `requirements.txt` file at the root level, or just let `setup.py` do it's thing.

## Some extra stuff

* Tests are automatically skipped if no tests are found
* Tests have to be in files following the pattern `test*.py`
* If the code changes are from a pull-request, a comment in the discussion about the test results will be made
* Take a look at [shields.io](shields.io) and search for 'github'. You'll get an idea of what badges in your readme can be used for!
