Quick script to show setting tags on projects by extracting a value from the projects target (ie, repository).

Install pyenv:

```bash
> brew install pyenv
# follow pyenv env setup steps
# then install 3.9.10
> pyenv install 3.9.10

# then for your system root / default for everything, set "local" python version in your home folder
> cd ~
> pyenv local 3.9.10

❯ which python
/Users/chris/.pyenv/shims/python
❯ python --version
Python 3.9.10
```

Install poetry and follow its shell setup instructions:

```bash
curl -sSL https://install.python-poetry.org | python -

# post shell instructions, configure virtualenv in directories
poetry config virtualenvs.in-project true

```

Now you're ready to checkout the code and work on it:

```bash
git clone git@github.com:snyk-tech-services/tag_by_target.git
cd tag_by_target
poetry install
source .venv/bin/activate
```

If you have your snyk token exported to SNYK_TOKEN then running something like this should work:

```bash
❯ python tag_by_target.py --help
usage: tag_by_target.py [-h] --org-id ORG_ID [--integration INTEGRATION] [--attribute ATTRIBUTE] [--field-sep FIELD_SEP] [--field-num FIELD_NUM] [--tag-name TAG_NAME] [--strip-char STRIP_CHAR]

Generate a CSV of projects in a Snyk Organization

optional arguments:
  -h, --help            show this help message and exit
  --org-id ORG_ID       The organization ID from the Org's Setting panel
  --integration INTEGRATION
                        Integration Name: bitbucket-cloud, github-enterprise, etc.
  --attribute ATTRIBUTE
                        Which target attribute to tag the projects with
  --field-sep FIELD_SEP
                        Optional field separator
  --field-num FIELD_NUM
                        Which field to use
  --tag-name TAG_NAME   What is the tag's Key name, attribute value is used by default
  --strip-char STRIP_CHAR
                        Remove this character from the beginning the field if it is present

❯ python tag_by_target.py --org-id 39ddc762-b1b9-41ce-ab42-defbe4575bd6 --attribute displayName --integration github-enterprise
```
# tag-by-target
