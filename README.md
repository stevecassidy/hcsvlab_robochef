# HCSvLab RoboChef #

## Installation ##

```
git clone git@github.com:IntersectAustralia/hcsvlab_robochef.git
```

## Install the Dependencies ##

### OS X ###

These instructions assume you have [Homebrew](http://mxcl.github.com/homebrew/) installed


#### AntiWord ####

```
brew install antiword
```

Unfortunately, Homebrew doesn't install the resources correctly so you will have to fix this manually:

```
mv /usr/local/share/antiword/Resources/* /usr/local/share/antiword
rmdir /usr/local/share/antiword/Resources
```

#### Xpdf ####

```
brew install xpdf
```

## Install the Python Libraries ##

Use [pip](http://www.pip-installer.org/) or [easy_install](https://pypi.python.org/pypi/setuptools) to install `pyparsing`, `xlrd`, and `rdflib`, e.g:

```
pip install "pyparsing<=1.5.7" xlrd rdflib httplib2
```

NOTE: `pyparsing` currently defaults to v2.0 which only works with Python 3

## Generating RDF with HCSvLab RoboChef ##

Edit the `config.ini` file to point to the corpora and the desired output directory, e.g:

```
CORPUS_BASEDIR = /Users/ilya/workspace/corpora/
CORPUS_OUTPUTDIR = /Users/ilya/workspace/corpora_processed/
```

Add the `hcsvlab_robochef` parent directory to your `PYTHONPATH`, e.g:

```
export PYTHONPATH=$PYTHONPATH:/Users/ilya/workspace/
```

Run `main.py` in the `hcsvlab_robochef` directory:

```
python main.py
```
